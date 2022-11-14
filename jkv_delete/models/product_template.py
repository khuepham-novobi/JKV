# -*- coding: utf-8 -*-
from odoo import fields, models, api
        

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    filename_id = fields.Many2one(ondelete='cascade')

    @api.multi
    def unlink(self):
        if not self.env.context.get('skip_detaching_product'):
            product_ids = self.mapped('product_variant_id.id')
            product_video = self.env.ref('jkv_delete.product_video')
            sale_lines = self.env['sale.order.line'].sudo().search([('product_id.id', 'in', product_ids)])
            sale_lines.write({'product_id': product_video.id})
            invoice_lines = self.env['account.invoice.line'].sudo().search([('product_id.id', 'in', product_ids)])
            invoice_lines.write({'product_id': product_video.id})
        res = super(ProductTemplate, self).unlink()
        return res
