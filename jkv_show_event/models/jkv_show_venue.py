from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import ValidationError
import logging
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT

class JKVShowVenue(models.Model):
    _name = 'jkv.show.venue'

    name = fields.Char(string='Show Name',required=True)
    show_number = fields.Integer(string='Show Number', required=True)
    show_location = fields.Char(string='Show Location')
    start_date = fields.Date(string='Start Date',default=fields.Date.context_today)
    end_date = fields.Date(string='End Date', default=fields.Date.context_today)

    _sql_constraints = [
        ('jkv_show_number_uniq', 'unique(show_number)', 'Show Number must be unique!'),
    ]
    
    @api.one
    @api.constrains('start_date', 'end_date')
    def _check_date(self):
        if self.start_date > self.end_date:
            raise ValidationError("Start Date must be less or equal than End Date")
        now = datetime.now()
        now = now.strftime(DEFAULT_SERVER_DATE_FORMAT)
        if self.end_date < now:
            raise ValidationError("End Date entered must be after current day")