from odoo import api, fields, models,  _
from datetime import datetime
import logging
from openerp.exceptions import ValidationError, Warning
class JKVRider(models.Model):
    _inherit = 'jkv.rider'
    
    @api.model
    def create(self,vals):
        if self.env.context.get('import_file',False):
        
            list_key = ['show_number','rider_name','rider_number','horse_name']
            for key in list_key:
                if not vals.get(key,False):
                    raise ValidationError("Show number, Rider number, Rider name, Horse name cannot leave empty")
  
            show_number = vals['show_number']
            show_id = self.env['jkv.show.venue'].search([('show_number','=',show_number)]).id
            
            if not show_id:
                show_id = self.env['jkv.show.venue'].create({'name':show_number,'show_number':show_number}).id
                
            #Rider
            rider_usef_number = vals.get('rider_usef_number',False)            
            domain_rider = [('is_rider','=',True)]
            rider = False
            if rider_usef_number:
                domain_rider += [('jkv_customer_usef_number','=',rider_usef_number)]                
                rider = self.env['res.partner'].sudo().search(domain_rider,limit=1)
                
            #If USEF# match
            rider_id = False
            
            #If Horse Name Match
            if not rider:
                rider = self.env['res.partner'].sudo().search([('is_rider','=',True),('horse_name','ilike',vals['horse_name'])],limit=1)

            #If alias name match
            if not rider:
                rider = self.env['res.partner'].sudo().search([('is_rider','=',True),('alias_name','ilike',vals['rider_name'])],limit=1)
            
            #If not match all, create a new rider
            if not rider:
                rider = self.env['res.partner'].create({'is_rider':True,'name':vals['rider_name'],'jkv_customer_usef_number':vals.get('rider_usef_number',False)})

            if rider:
                rider_id = rider.id
                
            if rider.name != vals['rider_name'] and rider:
                if rider.alias_name:
                    alias_name = rider.alias_name + ','+vals['rider_name']
                else:
                    alias_name = vals['rider_name']
                rider.sudo().write({'alias_name':alias_name})

            #rider_id = self.env['res.partner'].create({'jkv_type':'rider','name':vals['rider_name'],'jkv_customer_usef_number':vals.get('rider_usef_number',False)}).id
                
            #Owner
            owner_usef_number = vals.get('owner_usef_number',False)
            owner_name = vals.get('owner_name',False)
            
            domain_owner = [('is_owner','=',True)]
            if owner_name:
                domain_owner += [('name','=',owner_name)]            
            if owner_usef_number:
                domain_owner += [('jkv_customer_usef_number','=',int(owner_usef_number))]
                
            owner_id = False
            if owner_name or owner_usef_number:
                owner = self.env['res.partner'].sudo().search(domain_owner,limit=1)
                if not owner:
                    owner_id = self.env['res.partner'].create({'is_owner':True,'name':owner_name,'jkv_customer_usef_number':owner_usef_number}).id
                else:
                    owner_id = owner.id
            #Trainer
            trainer_usef_number = vals.get('trainer_usef_number',False)
            trainer_name = vals.get('trainer_name',False)
            
            domain_trainer = [('is_trainer','=',True)]
            if trainer_name:
                domain_trainer += [('name','=',trainer_name)]            
            if trainer_usef_number:
                domain_trainer += [('jkv_customer_usef_number','=',trainer_usef_number)]

            trainer_id = False
            if trainer_name or trainer_usef_number:
                trainer = self.env['res.partner'].sudo().search(domain_trainer,limit=1)
                if not trainer:
                    trainer_id = self.env['res.partner'].create({'is_trainer':True,'name':trainer_name,'jkv_customer_usef_number':trainer_usef_number}).id
                else:
                    trainer_id = trainer.id

            vals['rider_id'] = rider_id
            vals['owner_id'] = owner_id
            vals['trainer_id'] = trainer_id

        return super(JKVRider,self).create(vals)


