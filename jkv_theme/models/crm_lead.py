# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    name = fields.Char(required=False, index=True)
    first_name = fields.Char(string="First Name")
    last_name = fields.Char(string="Last Name")
    # event_date = fields.Date(string="Event Date", default=fields.Date.today())

    is_rider = fields.Boolean(string='Is Rider', default=False)
    is_trainer = fields.Boolean(string='Is Trainer', default=False)
    is_owner = fields.Boolean(string='Is Owner', default=False)
    is_event_producer_manager = fields.Boolean(string='Is Event Producer/Manger', default=False)

    @api.model
    def create(self, vals):
        if('first_name' in vals and 'last_name' in vals):
            vals['contact_name'] = "{} {}".format(vals['first_name'], vals['last_name'])
        return super(CrmLead, self).create(vals)