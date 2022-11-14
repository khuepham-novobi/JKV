# -*- coding: utf-8 -*-
from odoo import api, fields, models,  _


class JKVDownload(models.Model):
    _inherit = 'jkv.download'
    
    show_id = fields.Many2one('jkv.show.venue', string='Show', store=True, compute='_compute_download_reference_value')
    show_name = fields.Char(string='Show Name', store=True, compute='_compute_download_reference_value')
    class_id = fields.Many2one('jkv.class', string='Class Name', store=True, compute='_compute_download_reference_value')
    rider_number = fields.Integer(string='Rider Number', store=True, compute='_compute_download_reference_value')
    ride_number = fields.Integer(string='Ride Number', store=True, compute='_compute_download_reference_value')

    @api.depends('product_id')
    def _compute_download_reference_value(self):
        for download in self:
            if download.product_id:
                download.update({
                    'show_id': download.product_id.filename_id.show_id.id,
                    'show_name': download.product_id.filename_id.show_id.name,
                    'class_id': download.product_id.filename_id.class_id.id,
                    'rider_number': download.product_id.rider_number,
                    'ride_number': download.product_id.ride_number
                })
