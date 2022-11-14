# -*- coding: utf-8 -*-
from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)
        if res.filename_id and res.filename_id.show_id and res.filename_id.show_id.is_set_price_default == 'custom':
            res.list_price = res.filename_id.show_id.product_price
        return res
