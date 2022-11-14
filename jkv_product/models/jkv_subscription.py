from odoo import api, fields, models,SUPERUSER_ID, _
from odoo.exceptions import Warning, ValidationError
import logging
from datetime import datetime,timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class JKVSubscription(models.Model):
    _name = 'jkv.subscription'
    _description = 'Subscription'
    
    product_ids = fields.Many2many('product.template', string='Products', compute='_get_products')
    expiry_date = fields.Date(string='Expiry Date',required=True)
    user_id = fields.Many2one('res.users',string='User')
    show_id = fields.Many2one('jkv.show.venue',string='Show')
    all_shows = fields.Boolean(string='All shows',default=False)
    expiried = fields.Boolean(string='Expired',store=True,compute='_compute_expiry_date',inverse='_set_value',default=False)
    type = fields.Selection([('my_video','My videos'),('all_videos','Entire Show')],default="all_videos",required=True)
    
    @api.depends('expiry_date')
    def _compute_expiry_date(self):
        now = datetime.now()
        for record in self:
            expiry_date = datetime.strptime(record.expiry_date, DEFAULT_SERVER_DATE_FORMAT)
            if expiry_date < now:
                record.expiried = True
            else:                
                record.expiried = False
                
    def _set_value(self):
        return True
        
    @api.model
    def _check_subscription(self):
        records = self.search([])
        now = datetime.now()        
        for record in records:
            expiry_date = datetime.strptime(record.expiry_date, DEFAULT_SERVER_DATE_FORMAT)
            if expiry_date < now:                
                record.sudo().write({'expiried':True})
            else:                
                record.sudo().write({'expiried':False})
            


    def _get_products(self):
        for record in self:
            if record.type == 'all_videos':
                products = self.env['product.template'].sudo().search([('filename_id.show_id.id','=',record.show_id.id)])
                record.product_ids = [(6,0,products._ids)]
            else:                    
                if record.user_id.partner_id.mapping_videos:
                    for video in record.user_id.partner_id.mapping_videos:
                        if video.filename_id.show_id.id == record.show_id.id:
                            record.product_ids = [(4,video.id)]


class JKVLiveStreamSubscription(models.Model):
    _name = 'jkv.livestream.subscription'

    user_id = fields.Many2one('res.users', string='User')
    expiry_date = fields.Date(string='Expiry Date')
    is_expired = fields.Boolean(string='Expired?', store=True, compute='_compute_expiry_date', inverse='_set_value', default=False)

    @api.depends('expiry_date')
    def _compute_expiry_date(self):
        now = datetime.now()
        for record in self:
            expiry_date = datetime.strptime(record.expiry_date, DEFAULT_SERVER_DATE_FORMAT)
            if expiry_date < now:
                record.is_expired = True
            else:
                record.is_expired = False

    def _set_value(self):
        return True

    @api.model
    def _check_livestream_subscription(self):
        records = self.search([])
        now = datetime.now()
        for record in records:
            expiry_date = datetime.strptime(record.expiry_date, DEFAULT_SERVER_DATE_FORMAT)
            if expiry_date < now:
                record.sudo().write({'is_expired': True})
            else:
                record.sudo().write({'is_expired': False})
