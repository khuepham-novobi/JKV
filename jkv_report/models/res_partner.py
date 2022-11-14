# -*- coding: utf-8 -*-
from odoo import api, fields, models,  _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def get_customers(self):
        records = self.search([('user_ids','!=',False)])
        ids = []
        for record in records:
            user = record.user_ids[0]
            if user.has_group('base.group_portal'):
                ids.append(record.id)

        return {
            'name': 'Customer',
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_type': 'form',
            'view_mode': 'tree, form',
            'views': [(self.env.ref('jkv_report.view_res_partner_report_tree').id, 'tree'), (False, 'form')],
            'domain':[('id','in',ids)],
            'target': 'self',
        }

