# -*- coding: utf-8 -*-
from odoo import fields, models


class JKVDownload(models.Model):
    _inherit = 'jkv.download'

    product_id = fields.Many2one(ondelete='set null', required=False)
