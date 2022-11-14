# -*- coding: utf-8 -*-
from odoo import api, fields, models,  _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.osv import expression
import logging


class JKVShowVenue(models.Model):
    _inherit = 'jkv.show.venue'

    video_ids = fields.One2many('jkv.filename', 'show_id', string='Videos')

    is_set_price_default = fields.Selection([('default', 'Default'), ('custom', 'Custom')], string='Set Price as', default='default')

    product_price = fields.Float('Price', default=lambda r: float(r.env.ref('jkv_website_purchase.product_price').value))
    subscription_my_video = fields.Float('Price', default=lambda r: float(r.env.ref('jkv_website_purchase.subscription_my_video').value))
    subscription_all_videos = fields.Float('Price', default=lambda r: float(r.env.ref('jkv_website_purchase.subscription_all_videos').value))

    @api.onchange('is_set_price_default')
    def change_price_default(self):
        if self.is_set_price_default == 'default':
            self.product_price = float(self.env.ref('jkv_website_purchase.product_price').value)
            self.subscription_my_video = float(self.env.ref('jkv_website_purchase.subscription_my_video').value)
            self.subscription_all_videos = float(self.env.ref('jkv_website_purchase.subscription_all_videos').value)

    @api.onchange('product_price', 'subscription_my_video', 'subscription_all_videos')
    def change_price(self):
        if (self.is_set_price_default != 'custom' and
                (self.product_price != float(self.env.ref('jkv_website_purchase.product_price').value) or
                 self.subscription_my_video != float(self.env.ref('jkv_website_purchase.subscription_my_video').value) or
                 self.subscription_all_videos != float(self.env.ref('jkv_website_purchase.subscription_all_videos').value))):
            self.is_set_price_default = 'custom'

    @api.multi
    def write(self, vals):
        result = super(JKVShowVenue, self).write(vals)
        if 'product_price' in vals:
            for record in self:
                products = self.env['product.template'].sudo().search([('filename_id.show_id.id', '=', record.id)])
                products.write({'list_price': vals['product_price']})
        return result

    # For initializing when default prices are not yet set
    @api.model
    def init_default_price(self):
        records = self.sudo().search([('is_set_price_default', '=', 'default')])
        records.sudo().write({
            'product_price': float(self.env.ref('jkv_website_purchase.product_price').value),
            'subscription_my_video': float(self.env.ref('jkv_website_purchase.subscription_my_video').value),
            'subscription_all_videos': float(self.env.ref('jkv_website_purchase.subscription_all_videos').value)
        })
