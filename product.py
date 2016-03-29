# This file is part of account_invoice_subvention module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import PoolMeta


__all__ = ['Template']


class Template:
    __metaclass__ = PoolMeta
    __name__ = "product.template"

    @classmethod
    def __setup__(cls):
        super(Template, cls).__setup__()
        value = ('subvention', 'Subvention')
        if value not in cls.type.selection:
            cls.type.selection.append(value)
