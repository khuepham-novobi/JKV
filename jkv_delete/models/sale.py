# -*- coding: utf-8 -*-
from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    subscription_id = fields.Many2one(ondelete='set null')
    show_id = fields.Many2one(ondelete='set null')
