# -*- coding: utf-8 -*-
from odoo import api, fields, models,  _
from datetime import datetime
from odoo.osv import expression
import logging

class ResUsers(models.Model):
    _inherit = 'res.users'
    
    close_status = fields.Boolean(string='Close status',default=False)