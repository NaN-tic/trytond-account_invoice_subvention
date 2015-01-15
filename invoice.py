# This file is part of account_invoice_subvention module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from decimal import Decimal
from trytond.config import config
from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
from trytond.transaction import Transaction


__all__ = ['Invoice', 'InvoiceLine', 'AccountInvoiceSubvention']
__metaclass__ = PoolMeta
_STATES = {
    'readonly': Eval('state') != 'draft',
    }
_TYPE = [
    ('out_invoice', 'Invoice'),
    ('in_invoice', 'Supplier Invoice'),
    ('out_credit_note', 'Credit Note'),
    ('in_credit_note', 'Supplier Credit Note'),
    ]
_ZERO = Decimal('0.0')
DIGITS = int(config.get('digits', 'unit_price_digits', 4))


class Invoice:
    __name__ = 'account.invoice'
    subventions = fields.One2Many('account.invoice.subvention', 'invoice',
        'Subventions', states=_STATES, depends=['state'])
    subvention_amount = fields.Function(fields.Numeric('Subventions',
            digits=(16, Eval('currency_digits', 2)),
            depends=['currency_digits']),
        'get_subventions', searcher='search_total_amount')
    customer_amount = fields.Function(fields.Numeric('Customer Amount',
            digits=(16, Eval('currency_digits', 2)),
            depends=['currency_digits']),
        'get_subventions', searcher='search_total_amount')

    @classmethod
    def get_subventions(cls, invoices, names):
        result = {n: {i.id: _ZERO for i in invoices} for n in names}
        amount = cls.get_amount(invoices,
            ['untaxed_amount', 'tax_amount', 'total_amount'])
        if 'total_amount' in amount:
            for invoice in invoices:
                if invoice.subventions:
                    result['subvention_amount'][invoice.id] = sum(s.amount
                        for s in invoice.subventions)
                    result['customer_amount'][invoice.id] = (
                        amount['total_amount'][invoice.id] -
                        result['subvention_amount'][invoice.id])
        return result

    @fields.depends('subventions', 'total_amount')
    def on_change_subventions(self):
        changes = {
            'subvention_amount': _ZERO,
            'customer_amount': _ZERO,
            }
        if self.subventions:
            changes['subvention_amount'] = sum(s.amount if s.amount else _ZERO
                for s in self.subventions)
            changes['customer_amount'] = (self.total_amount -
                changes['subvention_amount'])
        return changes

    @fields.depends('subventions')
    def on_change_lines(self):
        changes = super(Invoice, self).on_change_lines()
        if self.subventions:
            changes['subvention_amount'] = sum(s.amount
                for s in self.subventions)
            changes['customer_amount'] = (changes['total_amount'] -
                changes['subvention_amount'])
        return changes


class InvoiceLine:
    __name__ = 'account.invoice.line'

    @classmethod
    def __setup__(cls):
        super(InvoiceLine, cls).__setup__()
        domain = ('type', '!=', 'subvention')
        if domain not in cls.product.domain:
            cls.product.domain.append(domain)


class AccountInvoiceSubvention(ModelSQL, ModelView):
    'Account Invoice Subvention'
    __name__ = 'account.invoice.subvention'
    _rec_name = 'description'
    invoice = fields.Many2One('account.invoice', 'Invoice', ondelete='CASCADE',
        states={
            'required': True,
            })
    product = fields.Many2One('product.product', 'Product',
        states={
            'required': True,
            },
        domain=[
            ('type', '=', 'subvention'),
            ],
        )
    description = fields.Text('Description', size=None, required=True)
    unit = fields.Many2One('product.uom', 'Unit',
        states={
            'required': True,
            'readonly': True,
            },
        )
    unit_digits = fields.Function(fields.Integer('Unit Digits'),
        'on_change_with_unit_digits')
    quantity = fields.Float('Quantity', required=True,
        digits=(16, Eval('unit_digits', 2)),
        depends=['unit_digits'])
    unit_price = fields.Numeric('Unit Price', digits=(16, DIGITS))
    currency_digits = fields.Function(fields.Integer('Currency Digits'),
        'on_change_with_currency_digits')
    currency = fields.Many2One('currency.currency', 'Currency',
        states={
            'required': True,
            'invisible': True,
            },
        depends=['invoice'])
    amount = fields.Function(fields.Numeric('Amount',
            digits=(16, Eval('_parent_invoice', {}).get('currency_digits',
                    Eval('currency_digits', 2))), depends=['currency_digits']),
        'on_change_with_amount')

    @staticmethod
    def default_unit_digits():
        return 2

    @staticmethod
    def default_currency_digits():
        Company = Pool().get('company.company')
        if Transaction().context.get('company'):
            company = Company(Transaction().context['company'])
            return company.currency.digits
        return 2

    @staticmethod
    def default_currency():
        Company = Pool().get('company.company')
        if Transaction().context.get('company'):
            company = Company(Transaction().context['company'])
            return company.currency.id

    @fields.depends('product', 'unit', 'quantity', 'description', 'currency',
        'invoice')
    def on_change_product(self):
        Product = Pool().get('product.product')
        res = {}

        party_context = {}
        if self.invoice and self.invoice.party:
            party = self.invoice.party
            if party.lang:
                party_context['language'] = party.lang.code

        if self.product:
            if not self.description:
                with Transaction().set_context(party_context):
                    res['description'] = Product(self.product.id).rec_name
            res['unit'] = self.product.default_uom.id
            res['unit_price'] = self.product.list_price_uom
        return res

    @fields.depends('unit')
    def on_change_with_unit_digits(self, name=None):
        if self.unit:
            return self.unit.digits
        return 2

    @fields.depends('currency')
    def on_change_with_currency_digits(self, name=None):
        if self.currency:
            return self.currency.digits
        return 2

    @fields.depends('quantity', 'unit_price', 'currency', 'product')
    def on_change_with_amount(self, name=None):
        if self.currency and self.quantity and self.unit_price:
            return self.currency.round(
                Decimal(str(self.quantity)) * self.unit_price)
