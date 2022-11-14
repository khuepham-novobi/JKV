from odoo import api, fields, models,  _
from odoo.exceptions import Warning, ValidationError
import logging

class JKVFindClass (models.TransientModel):
    _name = 'jkv.find.class'
    _description = 'Finding Class View'

    class_number = fields.Integer(string='Class Number')
    class_name = fields.Char(string='Class Name')

    @api.multi
    def find_class(self):

        domain = []

        if self.class_number:
            domain.append(('class_number','=',self.class_number))

        if self.class_name:
            domain.append(('name','ilike',self.class_name))

        return { 
            'name': _('Class Result'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'jkv.class',
            'domain': domain,
        }

    """
    @api.multi
    def find_class(self):

        class_obj = self.env['jkv.class'].search([('class_number','=',self.class_number)], limit=1)

        if class_obj:
            self.class_name = class_obj.name
            self.class_ids = [(6,0,class_obj.ids)]
        else:
            self.class_name = ''
            raise Warning(_('Do not have this Class in database!'))

        return {
            "type": "ir.actions.do_nothing",
        }

    @api.multi
    def save_class(self):

        if not self.class_number:
            raise ValidationError("Class Number is required!")

        if not self.class_name:
            raise ValidationError("Class Name is required!")

        class_obj = self.env['jkv.class'].search([('class_number','=',self.class_number)], limit=1)

        if class_obj:
            class_obj.write({'name':self.class_name})
        else:
            self.class_name = ''
            raise Warning(_('Do not have this Class in database!'))

        return {
            "type": "ir.actions.do_nothing",
        }

    @api.multi
    def delete_class(self):

        class_obj = self.env['jkv.class'].search([('class_number','=',self.class_number)], limit=1)

        if class_obj:
            self.class_number = 0
            self.class_name = ''
            class_obj.unlink()
        else:
            raise Warning(_('Do not have this Class in database!'))

        return {
            "type": "ir.actions.do_nothing",
        }
    """


