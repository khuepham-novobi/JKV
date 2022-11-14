# -*- coding: utf-8 -*-
from odoo import api, fields, models,  _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.osv import expression
import logging
import random

def random_token():
    # the token has an entropy of about 120 bits (6 bits/char * 20 chars)
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.SystemRandom().choice(chars) for i in xrange(20))
    
class JKVDownload(models.Model):
    _name = 'jkv.download'
    
    url = fields.Char(string='Video URL',required=True)
    downloaded = fields.Boolean(string='Downloaded',default=False)
    partner_id = fields.Many2one('res.partner',required=True,string='User')
    token = fields.Char(string='Token')
    product_id = fields.Many2one('product.template',string='Product',required=True)
    downloaded_on = fields.Date(string='Downloaded on')

    @api.multi
    def _prepare(self):
        for download in self:
            token = random_token()
            while self._retrieve_download(token):
                token = random_token()
            download.write({'token': token})
        return True
        
    @api.model
    def _retrieve_download(self, token):
        download = self.sudo().search([('token', '=', token)], limit=1)
        if not download:            
            return False        
        return download
