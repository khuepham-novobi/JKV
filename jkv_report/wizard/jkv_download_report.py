from odoo import api, fields, models,  _
from odoo.exceptions import Warning, ValidationError
import logging

class JKVDownloadReportConfirm (models.TransientModel):
    _name = 'download.report.confirm'
    
    is_exported = fields.Boolean(string="Is Exported", default=False)
    
    @api.multi
    def download_report(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        self.is_exported = True
        return {
            'type' : 'ir.actions.act_url',
            'url': '/download_record/export/?record_ids=%s'%(str(active_ids)),
            'target': 'self',
        }
        
class JKVDownloadReport (models.TransientModel):
    _name = 'jkv.download.report'
    _description = 'Finding Download View'

    user_id = fields.Many2one('res.users',string='User')
    show_id = fields.Many2one('jkv.show.venue',string='Show')
    downloaded_date = fields.Date(string='Date Of Purchase')
    token = fields.Char(string='Token')

    @api.multi
    def find_downloaded_videos(self):

        domain = []

        if self.user_id:
            domain.append(('partner_id.id','=',self.user_id.partner_id.id))
        if self.show_id:
            domain.append(('show_id.show_number','=',self.show_id.show_number))
        if self.downloaded_date:
            domain.append(('create_date','<=',self.downloaded_date))
        if self.token:
            domain.append(('token','=',self.token))

        return { 
            'name': _('Downloaded Videos Result'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'jkv.download',
            'domain': domain,
        }