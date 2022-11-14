# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    free_view = fields.Boolean(string='Free view', compute='_get_status', store=True)

    @api.depends('filename_id.show_id.end_date')
    def _get_status(self):
        now = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
        for record in self:
            if record.filename_id:
                end_date = record.filename_id.show_id.end_date
                record.free_view = end_date >= now
            else:
                record.free_view = False

    @api.model
    def _get_status_daily(self):
        records = self.env['product.template'].sudo().search([('filename_id', '!=', False)])
        records._get_status()
