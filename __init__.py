# This file is part of account_invoice_subvention module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from . import product
from . import invoice


def register():
    Pool.register(
        product.Template,
        invoice.Invoice,
        invoice.InvoiceLine,
        invoice.AccountInvoiceSubvention,
        module='account_invoice_subvention', type_='model')
