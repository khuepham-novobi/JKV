from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import ValidationError
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT


class EventCalendar(models.Model):
    _inherit = 'jkv.events.calendar'

    gsec_schedule = fields.Char(required=False)
    prize_list = fields.Char(required=False)
    start_date = fields.Date(string='Start Date', default=fields.Date.context_today)
    end_date = fields.Date(string='End Date', default=fields.Date.context_today)

    @api.one
    @api.constrains('start_date', 'end_date')
    def _check_date(self):
        if self.start_date > self.end_date:
            raise ValidationError("Start Date must be less or equal than End Date")
        now = datetime.now()
        now = now.strftime(DEFAULT_SERVER_DATE_FORMAT)
        if self.end_date < now:
            raise ValidationError("End Date entered must be after current day")

    @api.model
    def _format_date(self, date):
        month_switcher = {
            '01': 'JAN',
            '02': 'FEB',
            '03': 'MAR',
            '04': 'APR',
            '05': 'MAY',
            '06': 'JUNE',
            '07': 'JULY',
            '08': 'AUG',
            '09': 'SEPT',
            '10': 'OCT',
            '11': 'NOV',
            '12': 'DEC',
        }
        month = month_switcher.get(date[5:7], "Invalid month of years")
        if 4 <= int(date[8:10]) <= 20 or 24 <= int(date[8:10]) <= 30:
            day_suffix = "TH"
        else:
            day_suffix = ["ST", "ND", "RD"][int(date[8:10]) % 10 - 1]

        return month + " " + date[8:10] + day_suffix

    def compute_start_date(self):
        for i in range(len(self)):
            self[i].start_date_format = self[i]._format_date(self[i].start_date)

    def compute_end_date(self):
        for i in range(len(self)):
            self[i].end_date_format = self[i]._format_date(self[i].end_date)

    start_date_format = fields.Char(compute=compute_start_date, store=False)
    end_date_format = fields.Char(compute=compute_end_date, store=False)

