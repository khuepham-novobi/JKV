from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import ValidationError
import logging
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT

class JKVShowVenue(models.Model):
    _inherit = 'jkv.show.venue'

    filename_ids = fields.One2many('jkv.filename','show_id',string='Files')
    class_ids = fields.Many2many(compute='_get_class')
    rider_ids = fields.Many2many(compute='_get_rider')

    def _get_class(self):
        for record in self:
            if record.filename_ids:
                record.class_ids = [(6,0,[u.class_id.id for u in record.filename_ids])]
            else:
                record.class_ids = False

    def _get_rider(self):
        for record in self:
            if record.filename_ids:
                record.rider_ids = [(6, 0, [u.rider_id.id for u in record.filename_ids])]
            else:
                record.rider_ids = False
