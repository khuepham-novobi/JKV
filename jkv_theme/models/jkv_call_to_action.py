from odoo import api, fields, models, tools

class JKVCallToAction(models.Model):
    _name = "jkv.calltoaction"
    _rec_name = "name"

    name = fields.Char(string='Page Name', required=True)
    status = fields.Boolean(string='Show', required=True)
    status_on_view = fields.Char(compute='_status_on_view')

    def _status_on_view(self):
        for i in range(len(self)):
            self[i].status_on_view = 'ON' if self[i].status else 'OFF'
