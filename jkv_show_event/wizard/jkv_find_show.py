from odoo import api, fields, models,  _
from odoo.exceptions import Warning, ValidationError
from datetime import datetime
import logging

class JKVFindShow (models.TransientModel):
    _name = 'jkv.find.show'
    _description = 'Finding Show View'

    name = fields.Char(string='Show Name')
    show_number = fields.Integer(string='Show Number')
    show_location = fields.Char(string='Show Location')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')

    @api.multi
    def find_show(self):

        domain = []

        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError("Start Date must be less or equal than End Date")

        if self.show_number:
            domain.append(('show_number','=',self.show_number))

        if self.name:
            domain.append(('name','ilike',self.name))

        if self.show_location:
            domain.append(('show_location','ilike',self.show_location))

        if self.start_date:
            domain.append(('start_date','>=',self.start_date))

        if self.end_date:
            domain.append(('end_date','<=',self.end_date))

        return { 
            'name': _('Show Result'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'jkv.show.venue',
            'domain': domain,
        }

    """
    @api.multi
    def find_show(self):

        show_obj = self.env['jkv.show.venue'].search([('show_number','=',self.show_number)], limit=1)

        if show_obj:
            self.name = show_obj.name
            self.show_location = show_obj.show_location
            self.start_date = show_obj.start_date
            self.end_date = show_obj.end_date        
        else:
            raise Warning(_('Do not have this Show in database!'))

        return {
            "type": "ir.actions.do_nothing",
        }

    @api.multi
    def save_show(self):

        if not self.show_number:
            raise ValidationError("Show Number is required!")

        if not self.name:
            raise ValidationError("Show Name is required!")

        if not self.show_location:
            raise ValidationError("Show Location is required!")

        if not self.start_date:
            raise ValidationError("Start Date is required!")

        if not self.end_date:
            raise ValidationError("End Date is required!")

        if self.start_date > self.end_date:
            raise ValidationError("Start Date must be less or equal than End Date")

        show_obj = self.env['jkv.show.venue'].search([('show_number','=',self.show_number)], limit=1)

        if show_obj:
            show_obj.write({
                'name':self.name,
                'show_location': self.show_location,
                'start_date': self.start_date,
                'end_date': self.end_date,
                })
            self.show_number = 0
            self.name = ''
            self.show_location = ''
            self.end_date = False
            self.start_date = False
        else:
            raise Warning(_('Do not have this Show in database!'))

        return {
            "type": "ir.actions.do_nothing",
        }

    @api.multi
    def delete_show(self):

        show_obj = self.env['jkv.show.venue'].search([('show_number','=',self.show_number)], limit=1)

        if show_obj:
            self.show_number = 0
            self.name = ''
            self.show_location = ''
            self.end_date = False
            self.start_date = False
            show_obj.unlink()
        else:
            raise Warning(_('Do not have this Show in database!'))

        return {
            "type": "ir.actions.do_nothing",
        }
    """

