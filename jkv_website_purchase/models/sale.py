# -*- coding: utf-8 -*-
from odoo import api, fields, models,  _
import logging
from datetime import datetime,timedelta,date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import ValidationError
from odoo.tools import float_compare
from taxcloud_request import TaxCloudRequest

class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'
    
    # Get tax from TaxCloud API
    def get_tax_from_taxcloud(self, recipient_partner, tic_code, product_id=1):
        Param = self.env['ir.config_parameter'].sudo()
        api_id = Param.get_param('account_taxcloud.taxcloud_api_id')
        api_key = Param.get_param('account_taxcloud.taxcloud_api_key')
        request = TaxCloudRequest(api_id, api_key)

        shipper = self.company_id or self.env.user.company_id
        request.set_location_origin_detail(shipper)
        request.set_location_destination_detail(recipient_partner)

        request.set_items_detail(product_id, tic_code)

        res = request.get_tax()
        if res.get('error_message'):
            raise ValidationError(res['error_message'])
        return res
        
class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    @api.multi
    def validate_taxes_on_sales_order(self):
        Param = self.env['ir.config_parameter']
        api_id = Param.sudo().get_param('account_taxcloud.taxcloud_api_id')
        api_key = Param.sudo().get_param('account_taxcloud.taxcloud_api_key')
        request = TaxCloudRequest(api_id, api_key)

        shipper = self.company_id or self.env.user.company_id
        request.set_location_origin_detail(shipper)
        request.set_location_destination_detail(self.partner_shipping_id)

        request.set_order_items_detail(self)

        response = request.get_all_taxes_values()

        if response.get('error_message'):
            raise ValidationError(response['error_message'])

        tax_values = response['values']

        raise_warning = False
        for line in self.order_line:
            if not line.price_subtotal:
                tax_rate = 0.0
            else:
                tax_rate = tax_values[line.id] / line.price_subtotal * 100
            if float_compare(line.tax_id.amount, tax_rate, precision_digits=4):
                raise_warning = True
                tax = self.env['account.tax'].sudo().search([
                    ('amount', '=', tax_rate),
                    ('amount_type', '=', 'percent'),
                    ('type_tax_use', '=', 'sale')], limit=1)
                if not tax:
                    tax = self.env['account.tax'].sudo().create({
                        'name': 'Tax %s %%' % (tax_rate),
                        'amount': tax_rate,
                        'amount_type': 'percent',
                        'type_tax_use': 'sale',
                    })
                line.tax_id = tax
        if raise_warning:
            return {'warning': _('The tax rates have been updated, you may want to check it before validation')}
        else:
            return True
    @api.model
    def get_expiry_date(self,expiry_date_subscription,duration):    
        now = datetime.today()
        expiry_date_subscription = datetime.strptime(expiry_date_subscription,DEFAULT_SERVER_DATE_FORMAT)
        expiry_date = False
        if now < expiry_date_subscription:
            expiry_date = expiry_date_subscription + timedelta(days=int(duration))
            expiry_date = expiry_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
        else:
            expiry_date = now + timedelta(days=int(duration))
            expiry_date = expiry_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
        return expiry_date
        
    @api.multi
    def action_confirm(self):
        Subscription = self.env['jkv.subscription']
        LiveSubscription = self.env['jkv.livestream.subscription']
        res = super(SaleOrder,self).action_confirm()
        content = []
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        show_subscription_ids_all = {}
        show_subscription_ids_my = {}
        user_subscription_id = False
        partner = False
        for order in self:
            for line in order.order_line:
                if line.is_subscription:
                    if line.all_shows:
                        record = Subscription.sudo().search([('user_id.id','=',line.user_subscription_id.id),('all_shows','=',True)])
                        if record:
                            expiry_date = self.get_expiry_date(record.expiry_date,line.duration)                           
                            record.sudo().write({'expiry_date':expiry_date})
                        else:                            
                            Subscription.sudo().create({'all_shows':True,'user_id':line.user_subscription_id.id,'expiry_date':line.expiry_date})
                    else:
                        user_subscription_id = line.user_subscription_id.id
                        expiry_date = datetime.today() + timedelta(days=int(line.duration))
                        expiry_date = expiry_date.strftime(DEFAULT_SERVER_DATE_FORMAT)                        
                        if line.type_subscription == 'all_videos':
                            show_subscription_ids_all[line.show_id.id] = {'expiry_date':expiry_date,'duration':line.duration,'type':'all_videos'}
                        else:
                            show_subscription_ids_my[line.show_id.id] = {'expiry_date':expiry_date,'duration':line.duration,'type':'my_video'}
                        #Subscription.sudo().create({'all_shows':False,'user_id':line.user_subscription_id.id,'show_id':line.show_id.id,'expiry_date':line.expiry_date})
                elif line.is_livestream_subscription:
                    subscription = LiveSubscription.sudo().search([('user_id.id', '=', line.user_subscription_id.id)])
                    if subscription:
                        expiry_date = self.get_expiry_date(subscription.expiry_date, line.duration)
                        subscription.sudo().write({'expiry_date': expiry_date})
                    else:
                        LiveSubscription.sudo().create({'user_id': line.user_subscription_id.id, 'expiry_date': line.expiry_date})
                else:
                    product = line.product_id.product_tmpl_id
                    partner = order.partner_id
                    download = self.env['jkv.download'].sudo().search([('partner_id.id','=',partner.id),('product_id.id','=',product.id)],limit=1)
                    if not download:
                        download = self.env['jkv.download'].sudo().create({'partner_id':partner.id,'url':product.filename_id.video_filename_url,'product_id':int(product.id)})
                    else:
                        download.sudo().write({'downloaded':False})
                    download.sudo()._prepare()
                    URL = base_url + '/thank_you?token=' + download.token
                    content.append(URL)
                    
        if show_subscription_ids_all:
            keys = show_subscription_ids_all.keys()
            records = Subscription.sudo().search([('show_id.id','in',keys),('type','=','all_videos'),('all_shows','=',False),('user_id.id','=',user_subscription_id)])
            for record in records:
                expiry_date = self.get_expiry_date(record.expiry_date,show_subscription_ids_all[record.show_id.id]['duration'])
                record.sudo().write({'expiry_date':expiry_date})
                show_subscription_ids_all.pop(record.show_id.id)
            for key in show_subscription_ids_all:
                Subscription.sudo().create({'all_shows':False,'user_id':user_subscription_id,'show_id':key,'type':'all_videos','expiry_date':show_subscription_ids_all[key]['expiry_date']})
        
        if show_subscription_ids_my:
            keys = show_subscription_ids_my.keys()
            records = Subscription.sudo().search([('show_id.id','in',keys),('type','=','my_video'),('all_shows','=',False),('user_id.id','=',user_subscription_id)])
            for record in records:
                expiry_date = self.get_expiry_date(record.expiry_date,show_subscription_ids_my[record.show_id.id]['duration'])
                record.sudo().write({'expiry_date':expiry_date})
                show_subscription_ids_my.pop(record.show_id.id)
            for key in show_subscription_ids_my:
                Subscription.sudo().create({'all_shows':False,'user_id':user_subscription_id,'show_id':key,'type':'my_video','expiry_date':show_subscription_ids_my[key]['expiry_date']})
        # if content:
        #     email_to = partner.email
        #     template = self.env['ir.model.data'].sudo().get_object('jkv_website_purchase', 'send_link')
        #     mail_template_obj = self.env['mail.template']
        #     mail_template_obj._ids = [template.id]
        #     mail_template_obj.with_context(subject='JK Video Instructions',content=content,email_to=email_to).sudo().send_mail(self._uid,force_send=True, raise_exception=False,email_values=None)
        return res
        
                
    @api.multi
    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, attributes=None, **kwargs):
        res = super(SaleOrder,self)._cart_update(product_id=product_id,line_id=line_id,add_qty=add_qty,set_qty=set_qty,attributes=attributes,kwargs=kwargs)        
        line_id = res.get('line_id',False)
        quantity = res.get('quantity',0)
        if line_id and quantity >0:            
            line = self.env['sale.order.line'].sudo().browse(line_id)
            line.write({'product_uom_qty':1})
        return res
        
    @api.multi
    def _cart_find_product_line(self, product_id=None, line_id=None, **kwargs):
        product_subscription_id = self.env.ref('jkv_website_purchase.product_subscription').id
        lines = super(SaleOrder,self)._cart_find_product_line(product_id=product_id,line_id=line_id,kwargs=kwargs)
        if not kwargs:
            return lines
        kwargs = kwargs.get('kwargs')
        args = kwargs.get('args',{})
        many_show = args.get('many_show',False)
        all_shows = True if many_show == 'all_shows' else False
        show_id = args.get('show_id',0)
        type_subscription = args.get('type_subscription','all_videos')
        if product_id == product_subscription_id and args and not line_id:
            for line in lines:               
                if all_shows:
                    if line.all_shows:
                        return line
                else:
                    if line.show_id.id == int(show_id) and line.type_subscription == type_subscription:
                        return line
            return self.env['sale.order.line']
        else:
            return lines


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    is_subscription = fields.Boolean(string='For subscription',default=False)
    is_livestream_subscription = fields.Boolean(string='For Livestream subscription', default=False)
    subscription_id = fields.Many2one('jkv.subscription',string='Subscription')
    duration = fields.Selection([('7','7 days'),('30','30 days'),('90','90 days'),('365','365 days')])
    subscription_info = fields.Char(string='Info for subscription')
    show_id = fields.Many2one('jkv.show.venue',string='Show')
    all_shows = fields.Boolean(string='All shows',default=False)
    expiry_date = fields.Date(string='Expiried Date',store=True,compute='_get_expiry_date')
    user_subscription_id = fields.Many2one('res.users',string='Subscription for user')
    type_subscription = fields.Selection([('my_video','My videos'),('all_videos','All videos')],default="all_videos")
    
    @api.multi
    def _get_display_price(self, product):
        for line in self:
            if line.is_subscription or line.is_livestream_subscription:
                return line.price_unit
            return super(SaleOrderLine,self)._get_display_price(product)
            
    @api.depends('duration')
    def _get_expiry_date(self):
        for record in self:
            expiry_date = datetime.today() + timedelta(days=int(record.duration))
            record.expiry_date = expiry_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
            
    @api.multi
    def _compute_tax_id(self):
        try:
            res = super(SaleOrderLine,self)._compute_tax_id()
            return res
        except:
            return False
        
    
    

