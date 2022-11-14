# -*- coding: utf-8 -*-
from odoo import fields, models


class JKVSubscription(models.Model):
    _inherit = 'jkv.subscription'

    show_id = fields.Many2one(ondelete='cascade')
