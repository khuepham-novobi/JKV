# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

import re
from datetime import datetime
import logging
from contextlib import closing
import requests
from lxml import etree, objectify

import boto3
from botocore.exceptions import ClientError

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.website_portal.controllers.main import website_account
from odoo.addons.website.models.website import slug

from odoo.addons.website_sale_account_taxcloud.controllers.main import WebsiteSale as WebsiteSaleAccount
from odoo.addons.jkv_product.models.s3_helper import S3Helper

_logger = logging.getLogger(__name__)


class WebsiteSaleAccount(WebsiteSaleAccount):

    @http.route()
    def payment(self, **post):
        order = request.website.sale_get_order()
        if not order:
            return request.redirect("/shop")
        return super(WebsiteSaleAccount, self).payment(**post)


class WebsiteSaleExt(WebsiteSale):

    @http.route()
    def payment_confirmation(self, **post):
        sale_order_id = request.session.get('sale_last_order_id')
        res = super(WebsiteSaleExt,self).payment_confirmation(**post)
        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            flag_subscription = False
            for line in order.order_line:
                if line.is_subscription:
                    flag_subscription = True
                    break
            new_message = 'We have sent the link to your e-mail to download video(s).'
            if flag_subscription:
                new_message = 'We have sent the link to your e-mail to download video(s) and updated your subscription data.'
            
            res.qcontext.update({'new_message':new_message})
            return res
        return res

    @http.route()
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        uid = request.session.uid
        if not uid:
            return request.redirect("/web/login")
        return super(WebsiteSaleExt, self).cart_update(product_id=product_id, add_qty=add_qty, set_qty=set_qty, kw=kw)
    
    @http.route()
    def product(self, product, category='', search='', **kwargs):    
        res = super(WebsiteSaleExt,self).product(product=product,category=category,search=search,kwargs=kwargs)
        if not request.session.uid:
            return res
        product = res.qcontext.get('product')
        partner_id = request.env.user.partner_id.id
        URL = False
        download_record = request.env['jkv.download'].sudo().search([('product_id.id','=',product.id),('partner_id.id','=',partner_id)],limit=1)
        if download_record:
            URL = request.httprequest.url_root + 'thank_you?token=' + download_record.token
        res.qcontext.update({'download':URL})
        purchased_product = request.env['jkv.download'].sudo().search([('product_id.id', '=', product.id), ('partner_id.id', '=', partner_id)], limit=1)
        share_link = '{}shop/product/{}'.format(request.httprequest.host_url, slug(product)) if purchased_product else False
        res.qcontext.update({'share_link': share_link})
        return res
        
    @http.route()
    def payment_confirmation(self, **post):
        res = super(WebsiteSaleExt,self).payment_confirmation(**post)
        """sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            return request.redirect('/my/home')"""
        return res
        
class website_account(website_account):

    @http.route()
    def account(self, **kw):
        response = super(website_account, self).account(**kw)
        uid = request.session.uid
        user = request.env.user
        Subscription = request.env['jkv.subscription']
        Download = request.env['jkv.download']
        subscription_count = Subscription.search_count([('user_id.id','=',uid)])
        download_count = Download.search_count([('partner_id.id','=',user.partner_id.id)])
        response.qcontext.update({'subscription_count':subscription_count,'download_count':download_count})
        return response

        
    @http.route(['/my/purchased_videos', '/my/purchased_videos/page/<int:page>'], type='http', auth="user", website=True)
    def my_purchased_videos(self, page=1, **kw):
        values = self._prepare_portal_layout_values()
        user = request.env.user
        Download = request.env['jkv.download']
        domain = [('partner_id.id','=',user.partner_id.id)]       
        download_count = Download.search_count(domain)
    
        pager = request.website.pager(
            url="/my/purchased_videos",
            url_args={},
            total=download_count,
            page=page,
            step=self._items_per_page
        )
        records = Download.sudo().search(domain,limit=self._items_per_page, offset=pager['offset'])            
        values.update({'records':records,'pager': pager,'default_url': '/my/purchased_videos'})
        
        return request.render("jkv_website_purchase.my_purchased_videos",values)
    @http.route(['/my/subscriptions', '/my/subscriptions/page/<int:page>'], type='http', auth="user", website=True)
    def my_subscriptions(self, page=1, **kw):
        values = self._prepare_portal_layout_values()
        uid = request.session.uid
        if not uid:
            return request.redirect("/web/login?redirect=/my/subscriptions")
        Subscription = request.env['jkv.subscription']
        domain = [('user_id.id','=',uid)]
        subscription_count = Subscription.search_count(domain)        
        pager = request.website.pager(
            url="/my/subscriptions",
            url_args={},
            total=subscription_count,
            page=page,
            step=self._items_per_page
        )
        subscriptions = Subscription.sudo().search(domain,limit=self._items_per_page, offset=pager['offset'])            
        values.update({'subscriptions':subscriptions,'pager': pager,'default_url': '/my/subscriptions'})
        
        return request.render("jkv_website_purchase.my_subscriptions",values)
        
class WebsitePurchase(http.Controller):

    @http.route(['/help_download_on_iOS'], type='http', auth="public", website=True)
    def download_on_iOS(self,token=None):
        return request.render('jkv_website_purchase.help_download_on_iOS',{'token':token})

    @http.route(['/renew'],type='http', auth="user",website=True)
    def renew(self,**args):
        if request.httprequest.method == 'POST':
            params = request.params.copy()
            product_id = request.env.ref('jkv_website_purchase.product_subscription').id
            duration = params.get('duration',False)
            subscription_id = params.get('subscription_id',False)
            subscription = request.env['jkv.subscription'].sudo().browse(int(subscription_id))
            
            many_show = 'all_shows' if subscription.all_shows else ''
            show_id = subscription.show_id.id if not subscription.all_shows else False
            res = request.website.sale_get_order(force_create=1)._cart_update(
                product_id=int(product_id),
                add_qty=float(1),
                set_qty=float(0),
                attributes=None,
                args={'many_show':many_show,'show_id':show_id}
            )
            line_id = res.get('line_id')
            
            SaleOrderLine = request.env['sale.order.line']
            line = SaleOrderLine.sudo().browse(line_id)
            
            if many_show == 'all_shows':
                line.sudo().write({'user_subscription_id':request.session.uid,'is_subscription':True,'all_shows':True,'duration':duration})
            else:
                line.sudo().write({'user_subscription_id':request.session.uid,'is_subscription':True,'all_shows':False,'show_id':int(show_id),'duration':duration})
            
            return request.redirect("/shop/cart")
            
            """
            expiry_date = datetime.today() + timedelta(days=int(duration))
            expiry_date = expiry_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
            Subscription = request.env['jkv.subscription']
            Subscription._ids = [int(subscription_id)]
            Subscription.sudo().write({'expiry_date':expiry_date})
            return request.redirect("/my/subscriptions")
            """
        else:
            return request.render('jkv_website_purchase.renew',{'subscription_id':subscription_id})

    @http.route(['/renew_livestream_subscription'], type='http', auth="user", website=True)
    def renew(self, **args):
        if request.httprequest.method == 'POST':
            params = request.params.copy()
            livestream_product_id = request.env.ref('jkv_website_purchase.product_livestream_subscription').id
            subscription_id = params.get('livestream_subscription_id', False)
            subscription = request.env['jkv.livestream.subscription'].sudo().browse(int(subscription_id))
            duration = params.get('duration', False)

            res = request.website.sale_get_order(force_create=1)._cart_update(
                product_id=int(livestream_product_id),
                add_qty=float(1),
                set_qty=float(0),
                attributes=None,
            )

            line_id = res.get('line_id')
            line = request.env['sale.order.line'].sudo().browse(line_id)
            name = 'Livestream Subscription - Duration: 1 year'
            price = request.env.ref('jkv_website_purchase.subscription_livestream').value
            line.sudo().write({'price_unit': price, 'name': name,
                               'user_subscription_id': request.session.uid,
                               'is_livestream_subscription': True, 'duration': duration})

            return request.redirect("/shop/cart")

        return request.redirect("/")

    @http.route(['/thank_you'], type='http', auth="public", website=True)
    def thank_you_purchase(self, token, from_ios_page=None):
        download = request.env['jkv.download'].sudo().search([('token', '=', token)], limit=1)
        from_ios_page = True if from_ios_page else False
        if not download:
            return request.render('website.404')
        return request.render('jkv_website_purchase.thank_you', {'token': token, 'from_ios_page': from_ios_page})
        
    @http.route(['/sent_email'],type='http', auth="public",website=True)
    def sent_email_purchase(self):        
        return request.render('jkv_website_purchase.sent_email')

    @http.route(['/download'], type='json', auth="user")
    def download(self, token=None):
        def return_error(err_msg):
            _logger.error('Could not get the video from this download (%s)'
                          '\nGot this error instead: %s' % (download.id, str(err_msg)))
            return {
                'success': False,
                'msg': str(err_msg),
            }

        download = request.env['jkv.download'].sudo().search([('token', '=', token)], limit=1)
        if not download:
            return request.render('website.404')

        # Update Last Downloaded on
        downloaded_on = datetime.today().strftime(DEFAULT_SERVER_DATE_FORMAT)
        download.sudo().write({'downloaded': True, 'downloaded_on': downloaded_on})

        # Prepare video name
        ICP = request.env['ir.config_parameter'].sudo()
        video_extension = ICP.get_param('jkv_product.filename_extension_mp4')
        filename = download.product_id.filename_id
        horse_name = filename.rider_id.horse_name
        class_name = filename.class_id.name
        ride_num = 'Ride %s' % filename.ride_number
        video_name = '%s_%s_%s%s' % (horse_name, class_name, ride_num, video_extension)
        non_printable = r'[^!-~]'
        non_allowed_char = r'[\/:*?"<>|%,;=]'
        white_spaces = r'\s+'
        video_name = re.sub(non_allowed_char, ' ', re.sub(non_printable, ' ', video_name))
        video_name = re.sub(white_spaces, ' ', video_name).strip()

        # Generate Presigned URL for user to access the video within the specific amount of time
        video_filename = download.url.split('/')[-1]
        s3_helper = S3Helper(request.env)
        url = s3_helper.generate_presigned_get_object(
            video_filename,
            5 * 60,
            download=dict(filename=video_name, content_type='video/mp4')
        )
        if not url:
            return return_error('None')

        # Test download link wihout actually downloading the video
        with closing(requests.get(url, stream=True)) as partial_res:
            # Could be something like video not exist
            if partial_res.status_code != 200:
                try:
                    res_tree = objectify.fromstring(partial_res.text)
                    msg = res_tree.find('.//Message')
                    return return_error(msg)
                except etree.ParseError as e:
                    # Unexpected response from S3
                    return return_error(e)

        return {
            'success': True,
            'url': url,
            'video_name': video_name,
        }

    @http.route(['/purchase_video'], type='json', auth="user", website=True)
    def purchase_video(self, product_id):
        uid = request.session.uid
        product = request.env['product.template'].sudo().search([('id', '=', int(product_id))])
        try:
            partner_id = request.env.user.partner_id.id
            email_to = request.env.user.partner_id.email
            download = request.env['jkv.download'].sudo().create(
                {'partner_id': partner_id, 'url': product.filename_id.video_filename_url, 'product_id': int(product_id)})
            download.sudo()._prepare()
            URL = request.httprequest.url_root + 'thank_you?token=' + download.token
            template = request.env['ir.model.data'].sudo().get_object('jkv_website_purchase', 'send_link')
            mail_template_obj = request.env['mail.template']
            mail_template_obj._ids = [template.id]
            mail_template_obj.with_context(subject='JK Video Instructions', content=URL, email_to=email_to) \
                .sudo().send_mail(uid, force_send=True, raise_exception=False, email_values=None)
            return {
                'code': 200,
                'message': 'Success'
            }
        except:
            return {
                'code': 200,
                'message': 'Success'
            }
    
    @http.route(['/purchase_subscription'], type='http', auth="user",website=True)
    def purchase_subscription(self,**args):
        params = request.params.copy()
        if 'submit' in params and params['submit'] == 'true':

            # Livestream subscription ==================================================================================
            if params.get('livestream'):
                livestream_product_id = request.env.ref('jkv_website_purchase.product_livestream_subscription').id
                duration = params.get('duration', False)
                res = request.website.sale_get_order(force_create=1)._cart_update(
                    product_id=int(livestream_product_id),
                    add_qty=float(1),
                    set_qty=float(0),
                    attributes=None,
                )
                line_id = res.get('line_id')
                line = request.env['sale.order.line'].sudo().browse(line_id)
                name = 'Livestream Subscription - Duration: 1 year'
                price = request.env.ref('jkv_website_purchase.subscription_livestream').value
                line.sudo().write({'price_unit': price, 'name': name,
                                   'user_subscription_id': request.session.uid,
                                   'is_livestream_subscription': True, 'duration': duration})
            # ==========================================================================================================

            show_ids = request.httprequest.args.getlist('shows')
            product_id = request.env.ref('jkv_website_purchase.product_subscription').id
            duration = params.get('duration',False)
            many_show = params.get('many_show',False)
            all_videos = params.get('type_video','my_video')
            for show_id in show_ids:               
                show_id = int(show_id)
                res = request.website.sale_get_order(force_create=1)._cart_update(
                    product_id=int(product_id),
                    add_qty=float(1),
                    set_qty=float(0),
                    attributes=None,
                    args={'many_show':many_show,'show_id':show_id,'type_subscription':all_videos}
                )
                line_id = res.get('line_id')
                
                SaleOrderLine = request.env['sale.order.line']
                line = SaleOrderLine.sudo().browse(line_id)
                
                name = 'Subscription'
                
                if many_show == 'all_shows':
                    name = 'All shows - Duration: ' + str(duration) + ' days'
                else:
                    show = request.env['jkv.show.venue'].sudo().browse(int(show_id))
                    if all_videos == 'my_video':
                        name = 'Subscription: '+ show.name + ' - Type: My videos' + ' - Duration: 1 year'
                    else:
                        name = 'Subscription: '+ show.name + ' - Type: Entire Show' + ' - Duration: 1 year'

                #expiry_date = datetime.today() + timedelta(days=int(duration))
                #expiry_date = expiry_date.strftime(DEFAULT_SERVER_DATE_FORMAT)            
                if many_show == 'all_shows':
                    line.sudo().write({'name':name,'user_subscription_id':request.session.uid,'is_subscription':True,'all_shows':True,'duration':duration})
                else:
                    price = 0
                    """
                    if str(duration) == '7':
                        price = request.env.ref('jkv_website_purchase.subscription_7_days').value
                    elif str(duration) == '30':
                        price = request.env.ref('jkv_website_purchase.subscription_30_days').value
                    elif str(duration) == '90':
                        price = request.env.ref('jkv_website_purchase.subscription_90_days').value
                    else:
                        price = request.env.ref('jkv_website_purchase.subscription_1_year').value
                    """

                    if all_videos == 'my_video':
                        price = request.env.ref('jkv_website_purchase.subscription_my_video').value
                    else:
                        price = request.env.ref('jkv_website_purchase.subscription_all_videos').value

                    show = request.env['jkv.show.venue'].sudo().browse(int(show_id))
                    if all_videos == 'my_video':
                        price = show.subscription_my_video if show.subscription_my_video else price
                    else:
                        price = show.subscription_all_videos if show.subscription_all_videos else price

                    line.sudo().write({'type_subscription':all_videos,'price_unit':price,'name':name,'user_subscription_id':request.session.uid,'is_subscription':True,'all_shows':False,'show_id':int(show_id),'duration':duration})
            
            return request.redirect("/shop/cart")
        
        """
        show_records = shows = request.env.user.partner_id.show_ids
        shows_uid = []
        partner = request.env.user.partner_id
        string_search = partner.name
        if partner.alias_name:
            string_search += partner.alias_name
        
        for show in show_records:
            flag = False
            for video in show.video_ids:
                if not video.rider_id:
                    continue
                if string_search.find(video.rider_id.rider_name) != -1:
                    shows_uid.append(show)
        """
        all_videos = params.get('type_video','my_video')
        show_records = request.env['jkv.show.venue'].sudo().search([])
        subscription_data = request.env['jkv.subscription'].sudo().search([('expiried','=',True),('user_id.id','=',request.session.uid)])
        show_subscribed = [u.show_id.id for u in subscription_data]
        shows = []
        if all_videos == 'all_videos':
            for show in show_records:
                if show.id not in show_subscribed:
                    shows.append(show)
        else:
            show_records = request.env.user.partner_id.show_ids
            for show in show_records:
                if show.id not in show_subscribed:
                    shows.append(show)
        return request.render("jkv_website_purchase.purchase_subscription",{'shows':shows,'type_video':all_videos})
        
    
    #Return values
    #-1: You have no specific video for that show
    #1: The subscription is still  unexpired
    #0: Nothing
    
    @http.route('/check_show', type='json', auth='user', website=True,method="post")
    def check_show(self, show_id=None):
        Subscription = request.env['jkv.subscription']
        #Remove all shows
        """
        if not show_id:
            record = Subscription.sudo().search([('user_id.id','=',request.session.uid),('all_shows','=',True)])
            if record and not record.expiried:
                expiry_date = datetime.strptime(record.expiry_date, DEFAULT_SERVER_DATE_FORMAT)
                expiry_date = expiry_date.strftime('%m/%d/%Y')
                return {'code':1,'message':'Your subscription for this option is still unexpired (Expiry Date: '+expiry_date+')'}
            return {'code':0,'message':'Nothing'}
        """
        show = request.env['jkv.show.venue'].sudo().search([('id','=',int(show_id))])
        record = Subscription.sudo().search([('user_id.id','=',request.session.uid),('all_shows','=',False),('show_id.id','=',show.id)])
        if record and not record.expiried:
            expiry_date = datetime.strptime(record.expiry_date, DEFAULT_SERVER_DATE_FORMAT)
            expiry_date = expiry_date.strftime('%m/%d/%Y')
            return {'code':1,'message':'Your subscription for this option is still unexpired (Expiry Date: '+expiry_date+')'}
        partner = request.env.user.partner_id
        string_search = partner.name
        if partner.alias_name:
            string_search += partner.alias_name
            
        flag = False
        for video in show.video_ids:
            if not video.rider_id:
                continue
            if string_search.find(video.rider_id.rider_name) != -1:
                flag = True
                break
        if flag == False:
            return {'code':-1,'message':'You have no specific video for that show'}
        return {'code':0,'message':'Nothing'}
        
    @http.route('/get_shows', type='json', auth='user',method="post")
    def get_shows(self, all_videos):
        if not request.session.uid:
            return []
        show_records = request.env['jkv.show.venue'].sudo().search([])
        subscription_data = request.env['jkv.subscription'].sudo().search([('expiried','=',True),('user_id.id','=',request.session.uid)])
        show_subscribed = [u.show_id.id for u in subscription_data]
        result = []
        if all_videos:
            for show in show_records:
                if show.id not in show_subscribed:
                    result.append({'id':show.id,'name':show.name})
        else:
            show_records = request.env.user.partner_id.show_ids
            for show in show_records:
                if show.id not in show_subscribed:
                    result.append({'id':show.id,'name':show.name})
        return result
