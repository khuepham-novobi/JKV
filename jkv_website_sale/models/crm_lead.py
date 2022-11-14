# -*- coding: utf-8 -*-

import logging
from odoo.addons.base.res.res_partner import FormatAddress
from odoo import api, fields, models, _
from datetime import datetime, timedelta, date

class Lead(FormatAddress, models.Model):

    _inherit = 'crm.lead'

    @api.model
    def create(self,vals):
        res = super(Lead,self).create(vals)
        template = self.env.ref('jkv_website_sale.template_contact_us_mail_reponse')
        mycontext = {
            'sent_date' : datetime.today().strftime("%m/%d/%Y"),
            'contact_name' : res.contact_name,
            'email_from' : res.email_from,
            'subject' : res.name
        }
        template.sudo().with_context(mycontext).send_mail(res.user_id.id, force_send=True, raise_exception=False)
        return res