from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import Warning, ValidationError
import logging


class JKVRider(models.Model):
    _name = 'jkv.rider'
    _rec_name = 'rider_name'

    rider_id = fields.Many2one('res.partner', string='Rider', ondelete='restrict')
    rider_2nd_id = fields.Many2one('res.partner', string='Rider 2', ondelete='restrict')
    rider_number = fields.Integer(string='Rider Number')
    rider_name = fields.Char(string='Rider Name', related='rider_id.name')
    rider_2nd_name = fields.Char(string='Rider Name 2', related='rider_2nd_id.name')
    rider_usef_number = fields.Integer(string='Rider USEF Number', related='rider_id.jkv_customer_usef_number')
    horse_name = fields.Char(string='Horse Name')
    owner_id = fields.Many2one('res.partner', string='Owner Name',ondelete='restrict')
    owner_name = fields.Char(string='Owner Name',related='owner_id.name')
    owner_usef_number = fields.Integer(string='Owner USEF Number', related='owner_id.jkv_customer_usef_number')
    owner_number = fields.Integer(string='Owner Number')
    trainer_id = fields.Many2one('res.partner', string='Trainer Name',ondelete='restrict')
    trainer_name = fields.Char(string='Trainer Name',related='trainer_id.name')
    trainer_number = fields.Integer(string='Trainer Number')
    trainer_usef_number = fields.Integer(string='Trainer USEF Number',related='trainer_id.jkv_customer_usef_number')
    barn = fields.Char(string='Barn')

    show_number = fields.Integer(string='Show Number')

    @api.constrains('rider_name', 'rider_number', 'rider_id','show_number')
    def _check_contraint(self):
        records = self.search([('rider_name','=', self.rider_name),('rider_number', '=', self.rider_number),('show_number','=',self.show_number)], limit=2)
        if len(records) >=2:
            raise ValidationError('Rider Name, Rider Number is a unique combination!')


