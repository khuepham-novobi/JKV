# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
import werkzeug
from itertools import groupby
from operator import itemgetter
import json

from odoo import http, _
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.web.controllers.main import ensure_db, Home
from odoo.addons.website_portal.controllers.main import website_account
from odoo.http import request,Response

_logger = logging.getLogger(__name__)

SUPPORTED_COUNTRY_CODES = [
    'AR',
    'AU',
    'BR',
    'CA',
    'ES',
    'IT',
    'MX',
    'NZ',
    'RU',
    'US',
]


class website_account(website_account):
    OPTIONAL_BILLING_FIELDS = ["zipcode", "state_id", "vat", "company_name","jkv_customer_number","jkv_customer_usef_number","receive_email","jkv_type"]
    
    def details_form_validate(self, data):
        error, error_message = super(website_account,self).details_form_validate(data)
        
        if data.get('jkv_customer_usef_number',False):
            try:
                value = int(data['jkv_customer_usef_number'])
            except:
                error['jkv_customer_usef_number'] = 'error'
                error_message.append(_('USEF Number entered must be an integer'))
                
        return error, error_message
        

class AuthSignupHome(Home):

    def get_auth_signup_qcontext(self):
        qcontext = super(AuthSignupHome,self).get_auth_signup_qcontext()
        params = request.params.copy()
        if 'error' in qcontext:
            return qcontext
        if params.get('password',False) != params.get('confirm_password',False):
            qcontext['error'] = _("Passwords do not match; please retype them.")
            return qcontext
        if qcontext.get('customer_usef_number',False):
            try:
                value = int(qcontext['customer_usef_number'])
            except:
                qcontext['error'] = _("USEF Number entered must be an integer")
                return qcontext
        if qcontext.get('token'):
            qcontext['email'] = request.env['res.partner']._signup_retrieve_partner(qcontext.get('token'), raise_exception=True).email
        return qcontext
        
        
    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):
        uid = request.session.uid
        if not uid:
            return super(AuthSignupHome,self).web_client(s_action=s_action,kw=kw)
        user = request.env['res.users'].sudo().search([('id','=',uid)],limit=1)
        if not user.has_group('base.group_user'):
            return werkzeug.utils.redirect('/shop', 303)
        return super(AuthSignupHome,self).web_client(s_action=s_action,kw=kw)
    
    
    @http.route('/remove_account', type='json', auth='user', website=True,method="post")
    def remove_account(self, password):
        uid = request.session.uid
        if uid == 1:
            return {'code':100,'message':'Cannot remove this account'}
        user = request.env['res.users'].sudo().search([('id','=',uid)])
        try:
            user.sudo(uid).check_credentials(password)            
            partner = user.partner_id
            record = request.env['jkv.rider'].sudo().search(['|',('rider_id.id','=',partner.id),'|',('trainer_id.id','=',partner.id),('owner_id.id','=',partner.id)],limit=1)
            subscriptions = request.env['jkv.subscription'].sudo().search([('user_id.id','=',uid)])
            user.sudo().unlink()
            for e in subscriptions:
                e.sudo().unlink()
            if not record:
                partner.sudo().unlink()
            else:
                partner.sudo().write({'active':False})
            
            request.session.logout(keep_db=True)
            return {'code':200,'message':'Success'}
        except Exception as e:
            logging.error(e)
            return {'code':100,'message':'Please try again. The password you provided is not correct'}

    
    @http.route('/web/signup', type='http', auth='public', website=True)
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()

        countries = request.env['res.country'].sudo().search([('code', 'in', SUPPORTED_COUNTRY_CODES)])
        states = request.env['res.country.state'].sudo().search(
            [('country_id.id', 'in', countries.ids)]
        )
        if request.params.get('detection_redirect',False) and request.httprequest.method == 'GET':
            lines = request.httprequest.args.getlist('lines')
            if lines:
                uid = request.session.uid
                user = request.env['res.users'].sudo().search([('id','=',uid)],limit=1)
                partner = user.partner_id
                ids = [int(u) for u in lines]
                partners = request.env['res.partner'].sudo().search([('id','in',ids)])
                alias_name = ''
                for p in partners:
                    alias_name = p.name + ', ' + alias_name if p.name else alias_name
                    partner.mapping_partner_ids = [(4, p.id)]
                
                partner.sudo().write({'alias_name':alias_name})
                    
            return http.redirect_with_hash(request.params['detection_redirect'])            
        
        if 'error' not in qcontext and request.httprequest.method == 'POST':
            params = request.params.copy()
            customer_usef_number = params['customer_usef_number']
            name = params['name']
            street = params.get('street',False)
            phone = params.get('phone',False)
            city = params.get('city',False)
            type_rider = params.get('type_rider',False)
            type_trainer = params.get('type_trainer',False)
            type_owner = params.get('type_owner',False)
            state_id = params.get('state_id',False)
            country_id = params.get('country_id',False)
            zip = params.get('zip_code',False)
            email = params.get('email',False)
            receive_email = params.get('receive_email',False)
                
            if customer_usef_number:
                res = super(AuthSignupHome, self).web_auth_signup(*args, **kw)
                uid = request.session.uid
                user = request.env['res.users'].sudo().search([('id','=',uid)],limit=1)
                partner_new = user.partner_id
                if res.qcontext.get('error'):
                    if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                        res.qcontext['error'] = _("Another user is already registered using this username.")
                        res.qcontext.update({'states': states, 'countries': countries})
                        return res
                partner_new.sudo().write({'customer_usef_number':customer_usef_number,'zip':zip,'country_id':country_id,'street':street,'phone':phone,'city':city,'state_id':state_id,'email':email,'receive_email':receive_email,'jkv_customer_usef_number':customer_usef_number})
                res.qcontext.update({'states': states, 'countries': countries})
                partners = request.env['res.partner'].sudo().search([('jkv_customer_usef_number','=',customer_usef_number)])
                if partners:
                    for partner in partners:
                        partner_new.mapping_partner_ids = [(4,partner.id)]
                        if partner.jkv_type == 'rider':
                            partner_new.sudo().write({'is_rider':True})
                        if partner.jkv_type == 'trainer':
                            partner_new.sudo().write({'is_trainer':True})
                        if partner.jkv_type == 'owner':
                            partner_new.sudo().write({'is_owner':True})

                        """
                        partner_new = user.partner_id
                        user.sudo().write({'partner_id':partner.id,'name':params['name']})
                        user.partner_id.sudo().write({'zip':zip,'country_id':country_id,'street':street,'phone':phone,'city':city,'state_id':state_id,'email':email,'receive_email':receive_email,'jkv_customer_usef_number':customer_usef_number})
                        partner_new.sudo().unlink()
                        """
                return res

            if not type_rider or not type_trainer or not type_owner:
                res = super(AuthSignupHome, self).web_auth_signup(*args, **kw)
                if res.qcontext.get('error'):
                    if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                        res.qcontext['error'] = _("Another user is already registered using this username.")
                        res.qcontext.update({'states': states, 'countries': countries})
                        return res
                uid = request.session.uid
                user = request.env['res.users'].sudo().search([('id','=',uid)],limit=1)
                user.partner_id.sudo().write({'zip':zip,'country_id':country_id,'street':street,'phone':phone,'city':city,'receive_email':receive_email,'state_id':state_id,'email':email,'jkv_customer_usef_number':customer_usef_number})
                res.qcontext.update({'states': states, 'countries': countries})
                return res        
  
            name_search = name[:3] if len(name) > 3 else name
            name = name.split()
            first_name = False
            last_name = False
            if len(name) == 2:
                first_name = name[0]
                last_name = name[1]
            domain = [('name','ilike',name_search)]
            if last_name:
                domain = ['&',('jkv_last_name','ilike',last_name),'|',('jkv_first_name','ilike',first_name[0]),('name','ilike',name_search)]
            records = request.env['res.partner'].sudo().search(domain)
            results = []
            
            res = super(AuthSignupHome, self).web_auth_signup(*args, **kw)
            if res.qcontext.get('error'):
                if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                    res.qcontext['error'] = _("Another user is already registered using this username.")
                return res

            uid = request.session.uid
            user = request.env['res.users'].sudo().search([('id','=',uid)],limit=1)
            partner_new = user.partner_id
            is_rider = True if type_rider else False
            is_trainer = True if type_trainer else False
            is_owner = True if type_owner else False
            partner_new.sudo().write({'zip':zip,'country_id':country_id,'street':street,'phone':phone,'city':city,'state_id':state_id,'is_rider':is_rider,'is_owner':is_owner,'is_trainer':is_trainer,'email':email,'receive_email':receive_email,'jkv_customer_usef_number':customer_usef_number})
            
            for record in records:
                if record.name.startswith(name_search):
                    results.append(record.id)
                if first_name:
                    if record.jkv_first_name.startswith(first_name[0]):
                        results.append(record.id)

            if results:
                lines_trainer = []
                lines_owner = []
                lines_rider = []
                if type_trainer:
                    records = request.env['jkv.rider'].sudo().search([('trainer_id.id','in',results)])                    
                    vals = []
                    for record in records:
                        id = record.trainer_id.id
                        horse_name = record.horse_name
                        if id not in vals:
                            lines_trainer.append({'id':id,'horse_name':horse_name})
                            vals.append(id)
                if type_owner:
                    records = request.env['jkv.rider'].sudo().search([('owner_id.id','in',results)])
                    vals = []
                    for record in records:
                        id = record.owner_id.id
                        name = record.owner_id.name
                        horse_name = record.horse_name
                        if id not in vals:
                            lines_owner.append({'id':id,'horse_name':horse_name})
                            vals.append(id)
                if type_rider:
                    records = request.env['jkv.filename'].sudo().search([('rider_id.rider_id.id','in',results)])
                    vals = []
                    for record in records:
                        id = record.rider_id.rider_id.id
                        name = record.rider_id.rider_name
                        rider_number = record.rider_number
                        show_name = record.show_id.name
                        if id not in vals:
                            lines_rider.append({'id':id,'name':name,'rider_number':rider_number,'show_name':show_name})
                            vals.append(id)
                context = {}
                type = []
                if lines_trainer:
                    type.append('trainer')
                    context.update({'lines_trainer': lines_trainer})
                if lines_owner:
                    type.append('owner')
                    context.update({'lines_owner': lines_owner})
                if lines_rider:
                    type.append('rider')
                    context.update({'lines_rider': lines_rider})
                if context:
                    context.update({'type': type})
                    return request.render('jkv_signup.detection', context)
            res.qcontext.update({'states': states, 'countries': countries})
            return res
            
        res = super(AuthSignupHome, self).web_auth_signup(*args, **kw)
        res.qcontext.update({'states': states, 'countries': countries, 'redirect': '/shop'})
        return res
