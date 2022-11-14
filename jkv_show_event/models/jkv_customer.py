from odoo import api, fields, models,  _
from datetime import datetime
import logging

class ResPartner(models.Model):
    _inherit = 'res.partner'

    jkv_customer_number = fields.Integer(string='Customer Number')
    jkv_customer_usef_number = fields.Integer(string='Customer USEF Number', default=0)
    jkv_type = fields.Selection([('rider', 'Rider'),('trainer', 'Trainer'),('owner','Owner')],string='Type')
    
    jkv_first_name = fields.Char(string='First Name')
    jkv_last_name = fields.Char(string='Last Name')
    name = fields.Char(compute='_compute_jkv_name', store=True, inverse='_inverse_jkv_name')
    
    jkv_save_filter = fields.Boolean(strng='Save My Filter', default=False)
    jkv_last_filter_video_ids = fields.Many2many('product.template', 'partner_product_last_filter_video_rel', 'partner', 'product', string='JKV Last Filter Videos')

    @api.depends('jkv_first_name', 'jkv_last_name')
    def _compute_jkv_name(self):
        for partner in self:
            if partner.jkv_first_name and partner.jkv_last_name:
                partner.name = partner.jkv_first_name + ' ' + partner.jkv_last_name
            else:
                partner.name = partner.jkv_first_name if partner.jkv_first_name else partner.jkv_last_name
                
    def _inverse_jkv_name(self):
        for partner in self:            
            name = partner.name.split()
            if len(name) == 2:
                partner.jkv_first_name = name[0]
                partner.jkv_last_name = name[1]
            else:
                partner.jkv_first_name = partner.name
                partner.jkv_last_name = ''
                    
    @api.model
    def create(self,vals):
        if not vals.get('jkv_customer_number',False):
            vals['jkv_customer_number'] = self.env['ir.sequence'].next_by_code('customer.number')
        return super(ResPartner,self).create(vals)
        