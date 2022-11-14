from odoo import api, fields, models


class JKVLiveStream(models.Model):
    _name = "jkv.livestream"

    name = fields.Char("Name")
    title = fields.Char(string="Title")
    license = fields.Char(string='License')
    source_url = fields.Char(string='URL')
    live_now = fields.Boolean(string='Live Now')
    page_url = fields.Char(string="Page URL")


