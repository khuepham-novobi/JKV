# -*- coding: utf-8 -*-
from odoo import api, fields, models,  _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.osv import expression
import logging
import random
    
class JKVSetPrice(models.TransientModel):
    _name = 'jkv.set.price'
    
    type = fields.Selection([('product','Product'),('subscription','Subscription')],required=True)
    duration = fields.Selection([('7','7 days'),('30','30 days'),('90','90 days'),('365','1 year')],default='365')
    price = fields.Float(string='Price',required=True)
    subscription_type = fields.Selection([('my_video','My videos'),('all_videos','Entire Show')],default="all_videos")
    
    @api.onchange('type','duration','subscription_type')
    def _on_change_type(self):
        if self.type == 'product':
            self.price = self.env.ref('jkv_website_purchase.product_price').value
        elif self.type == 'subscription':
            """
            if self.duration == '7':
                self.price = self.env.ref('jkv_website_purchase.subscription_7_days').value
            elif self.duration == '30':
                self.price = self.env.ref('jkv_website_purchase.subscription_30_days').value
            elif self.duration == '90':
                self.price = self.env.ref('jkv_website_purchase.subscription_90_days').value
            else:
                self.price = self.env.ref('jkv_website_purchase.subscription_1_year').value
            """
            if self.subscription_type == 'my_video':            
                self.price = self.env.ref('jkv_website_purchase.subscription_my_video').value
            else:
                self.price = self.env.ref('jkv_website_purchase.subscription_all_videos').value
        
    @api.multi
    def set_price(self, token):
        for record in self:
            if record.type == 'product':
                Product = self.env['product.template'].sudo()
                products = Product.search([])
                if products:
                    Product._ids = products._ids
                    Product.write({'list_price':record.price})
                    self.env.ref('jkv_website_purchase.product_price').sudo().write({'value':record.price})
            else:
                """
                if record.duration == '7':
                    parameter = self.env.ref('jkv_website_purchase.subscription_7_days')
                elif record.duration == '30':
                    parameter = self.env.ref('jkv_website_purchase.subscription_30_days')
                elif record.duration == '90':
                    parameter = self.env.ref('jkv_website_purchase.subscription_90_days')
                else:
                    parameter = self.env.ref('jkv_website_purchase.subscription_1_year')
                """
                if record.subscription_type == 'my_video':            
                    parameter = self.env.ref('jkv_website_purchase.subscription_my_video')
                else:
                    parameter = self.env.ref('jkv_website_purchase.subscription_all_videos')

                parameter.sudo().write({'value':record.price})
                
                
