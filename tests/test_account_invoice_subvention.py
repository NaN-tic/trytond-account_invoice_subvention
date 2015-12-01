# This file is part of the account_invoice_subvention module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase


class AccountInvoiceSubventionTestCase(ModuleTestCase):
    'Test Account Invoice Subvention module'
    module = 'account_invoice_subvention'


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        AccountInvoiceSubventionTestCase))
    return suite