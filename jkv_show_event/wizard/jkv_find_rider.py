from odoo import api, fields, models,  _
from odoo.exceptions import Warning
import logging

class JKVFindRider (models.TransientModel):
    _name = 'jkv.find.rider'
    _description = 'Finding Rider View'

    rider_first_name = fields.Char(string='Rider First Name')
    rider_last_name = fields.Char(string='Rider Last Name')
    owner_first_name = fields.Char(string='Owner First Name')
    owner_last_name = fields.Char(string='Owner Last Name')
    trainer_first_name = fields.Char(string='Trainer First Name')
    trainer_last_name = fields.Char(string='Trainer Last Name')
    horse_name = fields.Char(string='Horse Name')
    rider_number = fields.Integer(string='Rider Number')

    @api.multi
    def find_rider(self):

        domain = []

        if self.rider_first_name:
            domain.append(('rider_id.jkv_first_name','ilike',self.rider_first_name))

        if self.rider_last_name:
            domain.append(('rider_id.jkv_last_name','ilike',self.rider_last_name))

        if self.owner_first_name:
            domain.append(('owner_id.jkv_first_name','ilike',self.owner_first_name))

        if self.owner_last_name:
            domain.append(('owner_id.jkv_last_name','ilike',self.owner_last_name))

        if self.trainer_first_name:
            domain.append(('trainer_id.jkv_first_name','ilike',self.trainer_first_name))

        if self.trainer_last_name:
            domain.append(('trainer_id.jkv_last_name','ilike',self.trainer_last_name))

        if self.horse_name:
            domain.append(('horse_name','ilike',self.horse_name))

        if self.rider_number:
            domain.append(('rider_number','=',self.rider_number))
            
        return { 
            'name': _('Rider Result'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'jkv.rider',
            'domain': domain,
        }