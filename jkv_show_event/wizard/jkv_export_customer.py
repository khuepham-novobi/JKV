from odoo import api, fields, models,  _
import logging

class JKVCustomerReportConfirm (models.TransientModel):
    _name = 'customer.report.confirm'
    
    is_exported = fields.Boolean(string="Is Exported", default=False)
    
    @api.multi
    def download_report(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        self.is_exported = True
        return {
            'type' : 'ir.actions.act_url',
            'url': '/customer_record/export/?record_ids=%s'%(str(active_ids)),
            'target': 'self',
        }