# -*- coding: utf-8 -*-

import logging
from odoo.addons.base.res.res_partner import FormatAddress
from odoo import api, fields, models, _
from datetime import datetime, timedelta, date


class Lead(FormatAddress, models.Model):

    _inherit = 'crm.lead'

    name = fields.Char(string='Subject')
    create_date = fields.Datetime('Create Date')
    email_from = fields.Char(string='Customer Email')
    contact_name = fields.Char(string='Customer Name')
    description = fields.Text(string='Question')

    @api.model
    def create(self, vals):
        res = super(Lead, self).create(vals)

        template = self.env.ref('jkv_customer_support.template_jkv_customer_support')
        mycontext = {
            'jkv_sent_date': datetime.today().strftime("%m/%d/%Y"),
            'contact_name': res.contact_name,
            'email_from': res.email_from,
            'phone': res.phone,
            'subject': res.name,
            'question': res.description
        }
        try:
            admin = self.env.ref('base.jkv_admin')
            mycontext['jkv_user_name'] = admin.partner_id.name
            template.sudo().with_context(mycontext).send_mail(admin.id, force_send=True, raise_exception=False)
        except:
            mycontext['jkv_user_name'] = res.user_id.partner_id.name
            template.sudo().with_context(mycontext).send_mail(res.user_id.id, force_send=True, raise_exception=False)
        return res
