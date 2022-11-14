from odoo import api, fields, models

class JKVBlog(models.Model):
    _name = "jkv.tag"
    _rec_name = "name"

    name = fields.Char(string='Name', required=True)