from odoo import api, fields, models,  _
from datetime import datetime
import logging

class JKVClass(models.Model):
    _name = 'jkv.class'

    name = fields.Char(string='Class Name', required=True)
    class_number = fields.Integer(string='Class Number', required=True)

    _sql_constraints = [
        ('jkv_class_number_uniq', 'unique(class_number)', 'Class Number must be unique!'),
    ]
