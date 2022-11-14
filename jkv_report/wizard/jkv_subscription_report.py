from odoo import api, fields, models,  _
from odoo.exceptions import Warning, ValidationError
import logging

class JKVSubscriptionReportConfirm (models.TransientModel):
    _name = 'subcription.report.confirm'
    
    is_exported = fields.Boolean(string="Is Exported", default=False)
    
    @api.multi
    def download_report(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        self.is_exported = True
        return {
            'type' : 'ir.actions.act_url',
            'url': '/subscription_record/export/?record_ids=%s'%(str(active_ids)),
            'target': 'self',
        }
        
class JKVSubscriptionReport (models.TransientModel):
    _name = 'jkv.subscription.report'
    _description = 'Finding Subscription View'

    user_id = fields.Many2one('res.users',string='User')
    show_id = fields.Many2one('jkv.show.venue',string='Show')
    all_shows = fields.Boolean(string='All shows',default=False)
    subscribed_date = fields.Date(string='Date Of Subscription')

    @api.multi
    def find_subscription(self):

        domain = []

        if self.user_id:
            domain.append(('user_id.id','=',self.user_id.id))
        if self.show_id:
            domain.append(('show_id.show_number','=',self.show_id.show_number))
        if self.all_shows:
            domain.append(('all_shows','=',self.all_shows))
        if self.subscribed_date:
            domain.append(('create_date','<=',self.subscribed_date))

        return { 
            'name': _('Subscription Result'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'jkv.subscription',
            'domain': domain,
        }