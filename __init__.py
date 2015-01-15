# This file is part of account_invoice_subvention module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from .product import *
from .invoice import *


def register():
    Pool.register(
        Template,
        Invoice,
        InvoiceLine,
        AccountInvoiceSubvention,
        module='account_invoice_subvention', type_='model')
