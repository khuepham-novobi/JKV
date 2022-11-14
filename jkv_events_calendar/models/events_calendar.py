# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, timedelta, date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import logging

class EventsCalendar(models.Model):

    _name = 'jkv.events.calendar'

    name = fields.Char(string='Events Calendar Name', required=True)
    filename = fields.Char(string='Filename')
    event_file = fields.Binary(string="Upload Events Calendar", attachment=True, help="This field holds the pdf file of Events")
    event_description = fields.Char(string='Description')
    day = fields.Integer(string="Event Day", compute="_get_event_day", store=True)
    month = fields.Char(string="Event Month", compute="_get_event_month", store=True)
    year = fields.Integer(string="Event Year", compute="_get_event_year", store=True)
    event_date = fields.Date(string="Event Date", default=fields.Date.context_today)


    @api.depends('event_date')
    def _get_event_day(self):
        for event in self:
            if event.event_date:
                date = datetime.strptime(event.event_date, DEFAULT_SERVER_DATE_FORMAT)
                event.day = date.day

    @api.depends('event_date')
    def _get_event_month(self):
        month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June', 'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
        for event in self:
            if event.event_date:
                date = datetime.strptime(event.event_date, DEFAULT_SERVER_DATE_FORMAT)
                event.month = month[date.month - 1]

    @api.depends('event_date')
    def _get_event_year(self):
        for event in self:
            if event.event_date:
                date = datetime.strptime(event.event_date, DEFAULT_SERVER_DATE_FORMAT)
                event.year = date.year