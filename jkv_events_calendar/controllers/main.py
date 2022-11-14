# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo import http,SUPERUSER_ID,tools, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
import logging

ppg = 6

class WebsiteSaleExt(WebsiteSale):

    @http.route([
        '/page/events-calendar',
        '/page/events-calendar/page/<int:page>',
    ], type='http', auth="public", website=True)
    def events_calendar(self, page=0, **kwargs):
        domain = []
        url = "/page/events-calendar"
        events = request.env['jkv.events.calendar'].search(domain)
        pager = request.website.pager(url=url, total=len(events), page=page, step=ppg, scope=7, url_args=kwargs)
        events = request.env['jkv.events.calendar'].sudo().search(domain, limit=ppg, offset=pager['offset'], order='event_date desc')
        values = {
            'pager' : pager,
            'events': events
        }

        logging.warning(str(pager))

        return request.render("jkv_events_calendar.theme_events_calencar", values)

    @http.route(['/page/events-calendar/events/<int:event_id>'], type='http', auth="public", website=True)
    def events_calendar_detail(self, event_id=0, **kwargs):
        event = request.env['jkv.events.calendar'].sudo().browse(event_id)
        values = {
            'event': event
        }
        return request.render("jkv_events_calendar.theme_events_calencar_detail", values)
