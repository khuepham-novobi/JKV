# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo import http,SUPERUSER_ID,tools, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import TableCompute , PPG , PPR
import time
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import logging
import ast
import math

from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website.models.website import slug
from odoo.addons.website_sale.controllers.main import TableCompute
from odoo.addons.theme_furnito.controllers.main import WebsiteSale

class WebsiteSaleExt(WebsiteSale):
        
    @http.route(['/close_status'], type='http', auth="user")
    def close_status(self,**post):
        uid = request.session.uid
        if uid:
            user = request.env['res.users'].sudo().search([('id','=',uid)])
            user.sudo().write({'close_status':True})
    
    def _get_search_domain(self, search, category, attrib_values):
        domain =  super(WebsiteSaleExt,self)._get_search_domain(search, category, attrib_values)
        domain += [('filename_id.id','!=',False)]
        return domain
        
    @http.route([
        '/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>'
    ], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='', ppg=False, website=True,**post):
        request.session['filter_url'] = False
        res = super(WebsiteSaleExt,self).shop(page=page,category=category,search=search,ppg=ppg,post=post)
        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = PPG
            post["ppg"] = ppg
        else:
            ppg = PPG
        user_id = request.session.uid
        partner_id = request.env.user.partner_id.id
        jkv_collapse = request.httprequest.args.get('jkv_collapse','collapse2')
        is_livestream_product = bool(request.params.get('is_livestream_product', False))
        ###Need to improve performance

        #UPDATE VALUE FOR FILTER PANEL
        list_rider_names = []
        list_rider_numbers = []
        list_horse_names = []
        livestream_show_ids = []
        products = []
        livestream_class_ids = []
        now = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
        #Push selected to the beginning of list
        if is_livestream_product:
            livestream_show_ids = request.env['jkv_livestream.show'].sudo().search_read([], ['id', 'name', 'show_number'],
                                                                        order='start_date DESC')
            livestream_recent_show = request.env['jkv_livestream.show'].sudo().search_read([('start_date', '<=', now)],
                                                                           ['id', 'name', 'show_number'],
                                                                           order='start_date DESC', limit=1)
            # Default most recent show
            if len(livestream_recent_show) > 0:
                products = request.env['product.template'].sudo().search(
                    [('livestream_show_id', '=', livestream_recent_show[0]['id']),
                     ('is_livestream_product', '=', is_livestream_product)])
                livestream_class_ids = request.env['jkv_livestream.class'].sudo().search_read(
                    [('id', 'in', [u.livestream_class_id.id for u in products])], ['id', 'name', 'class_number'],
                    order='name ASC')
            # class_ids = set((p.id, p.name, p.class_number) for p in products.mapped('livestream_class_id'))
        else:
            show_ids = request.env['jkv.show.venue'].sudo().search_read([],['id','name','show_number'],order='start_date DESC')
            recent_show = request.env['jkv.show.venue'].sudo().search_read([('start_date','<=',now)],['id','name','show_number'],order='start_date DESC',limit=1)
            #Default most recent show
            products = request.env['product.template'].sudo().search([('filename_id.show_id.id', '=', recent_show[0]['id'])])
            class_ids = request.env['jkv.class'].sudo().search_read([('id','in',[u.filename_id.class_id.id for u in products])],['id','name','class_number'],order='name ASC')
        riders = request.env['jkv.rider'].sudo().search_read([('id','in',[u.filename_id.rider_id.id for u in products])],['id','rider_name','rider_number','horse_name','list_ride_number'])
        for rider in riders:
            if rider['rider_name'] not in list_rider_names:
                list_rider_names.append(rider['rider_name'])
            if rider['rider_number'] not in list_rider_numbers:
                list_rider_numbers.append(rider['rider_number'])
            if rider['horse_name'] not in list_horse_names:
                list_horse_names.append(rider['horse_name'])
        
        ################################


        list_rider_names.sort()
        list_rider_numbers.sort()
        list_horse_names.sort()
        list_post_days_filter = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        url = "/shop"
        url_args = []
        if is_livestream_product:
            url_args = "?is_livestream_product=true"
        pager = self._pager(url=url, total=len(products), page=page, step=ppg, scope=7, url_args=url_args)
        if is_livestream_product:
            if len(livestream_recent_show) > 0:
                products = request.env['product.template'].sudo().search([('livestream_show_id', '=', livestream_recent_show[0]['id']),
                 ('is_livestream_product', '=', is_livestream_product)], limit=PPG, offset=pager['offset'])
        else:
            products = request.env['product.template'].sudo().search(
                [('filename_id.show_id.id', '=', recent_show[0]['id'])],
                limit=PPG, offset=pager['offset'])

        res.qcontext.update({'products': products, 'pager': pager,'bins': TableCompute().process(products, ppg)})

        """
        list_post_days_filter = []
        for day in days:
            if day in list_post_days:
                list_post_days_filter.append(day)
        """

        url = "/shop"
        #Changes 03/05/18
        #Set default most recent show
        livestream_subscription = request.env['jkv.livestream.subscription'].sudo().search(
            [('user_id.id', '=', request.session.uid)], limit=1)
        no_subscription = False
        if not livestream_subscription or livestream_subscription.is_expired:
            no_subscription = True
        if is_livestream_product:
            if len(livestream_recent_show) > 0:
                res.qcontext.update({
                    'livestream_show_ids': livestream_show_ids,
                    'livestream_class_ids': livestream_class_ids,
                    'livestream_selected_shows': [livestream_recent_show[0]],
                    'livestream_show_checked_ids': [livestream_recent_show[0]['id']],
                    'is_livestream_product': is_livestream_product,
                    'livestream_selected_classes': [],
                    'livestream_class_checked_ids': [],
                    'no_subscription': no_subscription
                })
            else:
                res.qcontext.update({
                    'livestream_show_ids': livestream_show_ids,
                    'livestream_class_ids': livestream_class_ids,
                    'livestream_selected_shows': [],
                    'livestream_show_checked_ids': [],
                    'is_livestream_product': is_livestream_product,
                    'livestream_selected_classes': [],
                    'livestream_class_checked_ids': [],
                    'no_subscription': no_subscription
                })
        else:
            res.qcontext.update({
                'show_ids': show_ids,
                'class_ids': class_ids,
                'selected_shows': [recent_show[0]],
                'show_checked_ids': [recent_show[0]['id']],
                'is_livestream_product': is_livestream_product,
                'selected_classes': [],
                'class_checked_ids': [],
                'no_subscription': False
            })
        res.qcontext.update({
            # 'show_ids': show_ids,
            # 'class_ids': class_ids,
            'rider_names': list_rider_names,
            'rider_numbers': list_rider_numbers,
            'post_days': list_post_days_filter,
            'horse_names': list_horse_names,
            'show_all_video': 'show_all_video',
            'rider_checked_names': [],
            'rider_checked_numbers': [],
            'post_checked_days': [],
            'horse_checked_names': [],
            'ride_checked_numbers': [],
            'product_subcribed_no_expire': [],
            'products_purchased': [],
            'download_url': [],
            'jkv_collapse': jkv_collapse,
            # 'selected_shows': [recent_show[0]],
            # 'selected_classes': [],
            # 'show_checked_ids': [recent_show[0]['id']],
            # 'class_checked_ids': []
        })
        
        if request.session.uid:
            subscriptions = request.env['jkv.subscription'].sudo().search([('user_id.id','=',user_id),('expiried','=',False)],order='expiry_date DESC')
            subscription_status = {}
            product_subcribed_no_expire = []
            for subscription in subscriptions:
                for product in subscription.product_ids:
                    product_subcribed_no_expire.append(product)
                    if product.id not in subscription_status:
                        subscription_status[product.id] = subscription

            res.qcontext.update({
                'subscriptions' : subscriptions,
                'subscription_status':subscription_status,
                'product_subcribed_no_expire' : product_subcribed_no_expire,
            })

            #For product purchased
            if is_livestream_product:
                products_purchased = []
                download_url = {}
                all_products_purchased = []
                if len(products) >0:
                    downloads = request.env['jkv.download'].sudo().search(
                        [('product_id.id', 'in', products._ids), ('partner_id.id', '=', partner_id)])

                    for download in downloads:
                        products_purchased.append(download.product_id)
                        download_url[
                            download.product_id.id] = request.httprequest.url_root + 'thank_you?token=' + download.token

                    all_products_purchased = request.env['jkv.download'].sudo().search(
                        [('product_id.id', 'in', products._ids), ('partner_id.id', '=', partner_id)])
                share_link_prefix = '{}shop/product/'.format(request.httprequest.host_url)
                res.qcontext.update({
                    'products_purchased': products_purchased,
                    'download_url': download_url,
                    'all_products_purchased': [p.product_id for p in all_products_purchased],
                    'share_link_prefix': share_link_prefix
                })
            else:
                downloads = request.env['jkv.download'].sudo().search([('product_id.id','in',products._ids),('partner_id.id','=',partner_id)])
                products_purchased = []
                download_url = {}
                for download in downloads:
                    products_purchased.append(download.product_id)
                    download_url[download.product_id.id] = request.httprequest.url_root + 'thank_you?token=' + download.token

                all_products_purchased = request.env['jkv.download'].sudo().search(
                    [('product_id.id', 'in', products._ids), ('partner_id.id', '=', partner_id)])
                share_link_prefix = '{}shop/product/'.format(request.httprequest.host_url)
                res.qcontext.update({
                    'products_purchased': products_purchased,
                    'download_url': download_url,
                    'all_products_purchased': [p.product_id for p in all_products_purchased],
                    'share_link_prefix': share_link_prefix
                })
            #Remove all shows
            """
            check_sub_all_show = False
            for subscription in subscriptions:
                if subscription.all_shows == True:
                    res.qcontext.update({
                        'check_subscription_all_show' : True,
                        'subscription_all_show' : subscription
                    })
            """

        #SOMETHING ABOUT SUBSCRIPTION BY HUNG.NGUYEN
        if request.session.get('showed_status',False):
            return res
        if not user_id or user_id == 1:
            return res
        user = request.env['res.users'].sudo().search([('id','=',user_id)])
        if user.close_status:
            return res
        records = request.env['jkv.subscription'].sudo().search([('user_id.id','=',user_id)])
        request.session['showed_status'] = True
        if not records:            
            res.qcontext.update({'show_status':True,'new_subscription':True,'content_status':'You should purchase a subscription or a video'})
        else:
            now = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
            for record in records:
                if record.expiry_date < now:
                    res.qcontext.update({'show_status':True,'new_subscription':False,'content_status':'Your subscription has already expired. Do you want to renew?'})
                    return res
                expiry_date = record.expiry_date
                expiry_date = datetime.strptime(expiry_date, DEFAULT_SERVER_DATE_FORMAT)
                timedelta = datetime.now() - expiry_date
                if timedelta.days > 0 and timedelta.days < 5:
                    res.qcontext.update({'show_status':True,'new_subscription':False,'content_status':'Your subscription will expire in less than 5 calendar days. Do you want to renew?'})
        return res

    @http.route(['/search_videos'], type='http', auth="public", website=True)
    def jkv_search_template(self, **kwargs):

        user_id = request.session.uid
        user = request.env['res.users'].sudo().search([('id','=',user_id)])
        partner = user.partner_id
        values = {
            'company': request.website.company_id,
            'user': user,
            'jkv_save_filter': partner.jkv_save_filter
        }

        if kwargs:            
            jkv_start_date_search_video = kwargs.get('jkv_start_date_search_video')
            jkv_end_date_search_video = kwargs.get('jkv_end_date_search_video')
            domain = [('filename_id','!=',False)]

            if jkv_start_date_search_video != '':
                domain.append(('filename_id.show_id.end_date','>=',jkv_start_date_search_video))
            if jkv_end_date_search_video != '':
                domain.append(('filename_id.show_id.start_date','<=',jkv_end_date_search_video))

            products = request.env['product.template'].sudo().search(domain)

            show_ids = []
            class_ids = []
            rider_numbers = []
            post_days = []
            horse_names = []
            jkv_products = []

            for product in products:

                if product.filename_id.show_id not in show_ids:
                    show_ids.append(product.filename_id.show_id)

                if product.filename_id.class_id not in class_ids:
                    class_ids.append(product.filename_id.class_id)

                if product.rider_number not in rider_numbers:
                    rider_numbers.append(product.rider_number)

                if product.horse_name not in horse_names:
                    horse_names.append(product.horse_name)

                #if product.post_day not in post_days:
                #    post_days.append(product.post_day)

                jkv_products.append(product.id)

            rider_numbers.sort()
            horse_names.sort()
            #days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            #list_post_days_filter = []
            list_post_days_filter = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            """
            for day in days:
                if day in post_days:
                    list_post_days_filter.append(day)
            """
            class_ids = sorted(class_ids, key=lambda class_id: class_id.name)
            show_ids = sorted(show_ids, key=lambda show_id: show_id.name)
            values.update({
                'show_ids': show_ids,
                'class_ids': class_ids,
                'rider_numbers': rider_numbers,
                'post_days': list_post_days_filter,
                'horse_names': horse_names,
                'jkv_start_date_search_video': jkv_start_date_search_video,
                'jkv_end_date_search_video': jkv_end_date_search_video
            })

        return request.render("jkv_website_sale.theme_search_videos", values)

    #Only for Advance search
    def _pager(self, url, total, page=1, step=30, scope=5, url_args=None):
        """ Generate a dict with required value to render `website.pager` template. This method compute
            url, page range to display, ... in the pager.
            :param url : base url of the page link
            :param total : number total of item to be splitted into pages
            :param page : current page
            :param step : item per page
            :param scope : number of page to display on pager
            :param url_args : additionnal parameters to add as query params to page url
            :type url_args : dict
            :returns dict
        """
        # Compute Pager
        page_count = int(math.ceil(float(total) / step))

        page = max(1, min(int(page if str(page).isdigit() else 1), page_count))
        scope -= 1

        pmin = max(page - int(math.floor(scope/2)), 1)
        pmax = min(pmin + scope, page_count)

        if pmax - pmin < scope:
            pmin = pmax - scope if pmax - scope > 0 else 1

        def get_url(page):
            _url = "%s/page/%s" % (url, page) if page > 1 else url
            if url_args:
                _url = _url + url_args.replace(url,'')
            return _url

        return {
            "page_count": page_count,
            "offset": (page - 1) * step,
            "page": {
                'url': get_url(page),
                'num': page
            },
            "page_start": {
                'url': get_url(pmin),
                'num': pmin
            },
            "page_previous": {
                'url': get_url(max(pmin, page - 1)),
                'num': max(pmin, page - 1)
            },
            "page_next": {
                'url': get_url(min(pmax, page + 1)),
                'num': min(pmax, page + 1)
            },
            "page_end": {
                'url': get_url(pmax),
                'num': pmax
            },
            "page_last": {
                'url': get_url(pmax),
                'num': pmax
            },
            "pages": [
                {'url': get_url(page), 'num': page} for page in xrange(pmin, pmax+1)
            ]
        }
        
    @http.route([
        '/search_videos/results',
        '/search_videos/results/page/<int:page>'
    ], type='http', auth="public", website=True)
    def jkv_search_videos_feature(self, page=0, category=None, search='', ppg=False,website=True, **kwargs):
        #Update url for Continue button:
        request.session['filter_url'] = request.httprequest.url
        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = PPG
        else:
            ppg = PPG
        show_numbers = request.httprequest.args.getlist('show_number')
        class_numbers = request.httprequest.args.getlist('class_number')
        rider_names = request.httprequest.args.getlist('rider_name')
        rider_numbers = request.httprequest.args.getlist('rider_number')
        post_days = request.httprequest.args.getlist('post_day')
        horse_names = request.httprequest.args.getlist('horse_name')
        ride_numbers = request.httprequest.args.getlist('ride_number')
        jkv_save_filter = request.httprequest.args.get('jkv_save_filter')
        jkv_view_last_filter = request.httprequest.args.get('jkv_view_last_filter')
        jkv_start_date_search_video = request.httprequest.args.get('jkv_start_date_search_video')
        jkv_end_date_search_video = request.httprequest.args.get('jkv_end_date_search_video')
        show_all_video = request.httprequest.args.get('show_all_video')
        subscribed_video_only = request.httprequest.args.get('subscribed_video_only')
        #Changes 03/05/18
        show_my_videos = request.httprequest.args.get('show_my_videos')

        jkv_collapse = request.httprequest.args.get('jkv_collapse','collapse2')
        keep = QueryURL('/search_videos/results', category=category and int(category), search=search, attrib=[], order=kwargs.get('order'),
                        show_number=show_numbers,class_number=class_numbers,rider_name=rider_names,rider_number=rider_numbers,post_day=post_days,
                        horse_name=horse_names,ride_number=ride_numbers,jkv_start_date_search_video=jkv_start_date_search_video,jkv_end_date_search_video=jkv_end_date_search_video,
                        show_all_video=show_all_video,subscribed_video_only=subscribed_video_only,jkv_collapse=jkv_collapse)
        
        # UPDATE CHECKBOX FOR LEFT PART
        """
        list_checked_show_numbers =[]
        list_checked_class_numbers = []
        list_checked_rider_names = []
        list_checked_rider_numbers = []
        list_checked_post_days = []
        list_checked_horse_names = []
   
        for show_number in show_numbers:
            list_checked_show_numbers.append(int(show_number))
        for class_number in class_numbers:
            list_checked_class_numbers.append(int(class_number))
        for rider_name in rider_names:
            list_checked_rider_names.append(rider_name)
        for rider_number in rider_numbers:
            list_checked_rider_numbers.append(int(rider_number))
        for post_day in post_days:
            list_checked_post_days.append(post_day)
        for horse_name in horse_names:
            list_checked_horse_names.append(horse_name)
        """

        show_numbers = list(map(lambda id:int(id),show_numbers))
        class_numbers = list(map(lambda id:int(id),class_numbers))

        values = {
            'rider_checked_names' : rider_names,
            'rider_checked_numbers' : rider_numbers,
            'post_checked_days' : post_days,
            'horse_checked_names': horse_names,
            'jkv_collapse' : jkv_collapse,
            'show_checked_ids': show_numbers,
            'class_checked_ids': class_numbers
        }

        user_id = request.session.uid
        user = request.env['res.users'].sudo().search([('id','=',user_id)])
        partner = user.partner_id

        subscriptions = request.env['jkv.subscription'].sudo().search([('user_id.id','=',user_id),('expiried','=',False)],order='expiry_date DESC')
        subscription_status = {}
        product_subcribed_no_expire = []
        for subscription in subscriptions:
            for product in subscription.product_ids:
                product_subcribed_no_expire.append(product)
                if product.id not in subscription_status:
                    subscription_status[product.id] = subscription

        values.update({
            'subscriptions' : subscriptions,
            'subscription_status':subscription_status,
            'product_subcribed_no_expire' : product_subcribed_no_expire,
        })
        
        #Remove all shows
        """
        check_sub_all_show = False
        for subscription in subscriptions:
            if subscription.all_shows == True:
                values.update({
                    'check_subscription_all_show' : True,
                    'subscription_all_show' : subscription
                })
        """
        
        products = []
        domain = list()
        domain.append(('filename_id', '!=', False))
        if jkv_start_date_search_video:
            domain.append(('filename_id.show_id.end_date','>=',jkv_start_date_search_video))
        if jkv_end_date_search_video:
            domain.append(('filename_id.show_id.start_date','<=',jkv_end_date_search_video))
        # GET VIDEO WHICH SEARCHED IN FORM BEFORE, BY DATE AND USER

        if show_all_video:
            values.update({'show_all_video':show_all_video})
        if subscribed_video_only:
            values.update({'subscribed_video_only': subscribed_video_only})

        #Changes 03/05/18
        if show_my_videos:
            values.update({'show_my_videos': show_my_videos})

        if subscribed_video_only:
            subscriptions = request.env['jkv.subscription'].sudo().search([('user_id.id','=',user_id)])
            videos_subcribed = []
            for subscription in subscriptions:
                if subscription.product_ids:
                    videos_subcribed = videos_subcribed + list(subscription.product_ids._ids)
            domain.append(('id','in',videos_subcribed))
        elif not subscribed_video_only and show_my_videos: #Changes 03/05/18 elif not subscribed_video_only and not show_all_video
            domain.append(('id','in',partner.mapping_videos._ids))

        if not show_my_videos and not subscribed_video_only:
            show_all_video = True

        # IF USER CHOOSE VIEW THE LAST FILTER
        if jkv_view_last_filter:
            domain = [('id','in',partner.jkv_last_filter_video_ids._ids)]
            products = partner.jkv_last_filter_video_ids

        # IF USER CHOSE CREATE A NEW FILTER
        # CREATE DOMAIN FOR SEARCHING
        else:
            if show_numbers:
                domain.append(('filename_id.show_id.id','in',show_numbers))
            if class_numbers:
                domain.append(('filename_id.class_id.id','in',class_numbers))
            if rider_names:
                domain.append('|')
                domain.append(('filename_id.rider_id.rider_id.name', 'in', rider_names))
                domain.append(('filename_id.rider_id.rider_2nd_id.name', 'in', rider_names))
            if rider_numbers:
                domain.append(('rider_number','in',rider_numbers))
            if horse_names:
                domain.append(('horse_name','in',horse_names))
            if post_days:
                domain.append(('post_day','in',post_days))

            products = request.env['product.template'].sudo().search(domain)

            if partner:
                if jkv_save_filter:
                    partner.write({'jkv_save_filter':True})
                    list_jkv_last_filter_videos = []
                    for product in products:
                        list_jkv_last_filter_videos.append(product.id)
                    partner.jkv_last_filter_video_ids = [(6,0,list_jkv_last_filter_videos)]
                else:
                    partner.write({'jkv_save_filter':False})
 
        pricelist_context = dict(request.env.context)
        if not pricelist_context.get('pricelist'):
            pricelist = request.website.get_current_pricelist()
            pricelist_context['pricelist'] = pricelist.id
        else:
            pricelist = request.env['product.pricelist'].browse(pricelist_context['pricelist'])

        request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)

        show_ids = request.env['jkv.show.venue'].sudo().search_read([],['id', 'name', 'show_number'],order='start_date DESC')
        selected_shows = list(filter(lambda show:show['id'] in show_numbers,show_ids))

        selected_show_objs = request.env['jkv.show.venue'].browse(show_numbers)

        data_class_ids = []
        data_rider_ids = []
        for u in selected_show_objs:
            data_class_ids.extend(u.class_ids._ids)
            data_rider_ids.extend(u.rider_ids._ids)

        class_ids = []
        if data_class_ids:
            class_ids = request.env['jkv.class'].sudo().search_read([('id','in',data_class_ids)],
                                                                ['id', 'name', 'class_number'], order='name ASC')
        else:
            class_ids = request.env['jkv.class'].sudo().search_read([],
                                                                    ['id', 'name', 'class_number'], order='name ASC')
        selected_classes = list(filter(lambda class_number:class_number['id'] in class_numbers,class_ids))

        # DATA FOR LEFT PART OF PAGE RESULT
        rider_fields = ['id', 'rider_name', 'rider_2nd_name', 'rider_number', 'horse_name', 'list_ride_number']
        if data_rider_ids:
            riders = request.env['jkv.rider'].sudo().search_read([('id', 'in', data_rider_ids)], rider_fields)
        else:
            riders = request.env['jkv.rider'].sudo().search_read([], rider_fields)

        list_rider_names = set(rider['rider_name'] for rider in riders)
        list_rider_2nd_names = set(rider['rider_2nd_name'] for rider in riders if rider['rider_2nd_name'])
        list_rider_names = sorted(list_rider_names.union(list_rider_2nd_names))
        list_rider_numbers = sorted(set(rider['rider_number'] for rider in riders))
        list_horse_names = sorted(set(rider['horse_name'] for rider in riders))

        list_post_days_filter = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        values.update({
            'show_ids': show_ids,
            'class_ids': class_ids,
            'rider_names': list_rider_names,
            'rider_numbers': list_rider_numbers,
            'post_days': list_post_days_filter,
            'horse_names': list_horse_names,
            'jkv_start_date_search_video': jkv_start_date_search_video,
            'jkv_end_date_search_video': jkv_end_date_search_video,
            'selected_shows': selected_shows,
            'selected_classes': selected_classes
        })

        url = "/search_videos/results"
        #pager = request.website.pager(url=url, total=len(products), page=page, step=PPG, scope=7, url_args=kwargs)
        pager = self._pager(url=url, total=len(products), page=page, step=ppg, scope=7, url_args=keep(url))
        
        products = request.env['product.template'].sudo().search(domain, limit=ppg, offset=pager['offset'])

        from_currency = request.env.user.company_id.currency_id
        to_currency = pricelist.currency_id
        compute_currency = lambda price: from_currency.compute(price, to_currency)

        values.update({
            'pager': pager,
            'products': products,
            'bins': TableCompute().process(products, PPG),
            'rows': PPR,
            'compute_currency': compute_currency,
            'keep': keep,
        })
        partner_id = request.env.user.partner_id.id
        downloads = request.env['jkv.download'].sudo().search([('product_id.id','in',products._ids),('partner_id.id','=',partner_id)])
        products_purchased = []
        download_url = {}
        for download in downloads:
            products_purchased.append(download.product_id)
            download_url[download.product_id.id] = request.httprequest.url_root + 'thank_you?token=' + download.token

        all_products_purchased = request.env['jkv.download'].sudo().search(
            [('product_id.id', 'in', products._ids), ('partner_id.id', '=', partner_id)])
        share_link_prefix = '{}shop/product/'.format(request.httprequest.host_url)
        values.update({
            'products_purchased': products_purchased,
            'download_url': download_url,
            'all_products_purchased': [p.product_id for p in all_products_purchased],
            'share_link_prefix': share_link_prefix
        })

        return request.render("website_sale.products", values)

    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):    
        res = super(WebsiteSaleExt,self).product(product=product,category=category,search=search,kwargs=kwargs)
        now = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
        res.qcontext.update({'current_date':now})
        product = res.qcontext.get('product')
        if product.free_view:
            res.qcontext.update({'subscription': True, 'not_play': False, 'free_view': True})
            return res
        user_id = request.session.uid        
        subscription = False
        if user_id == 1:
            res.qcontext.update({'subscription': True, 'not_play': False, 'free_view': False})
            return res
        if user_id:
            records = request.env['jkv.subscription'].sudo().search([('user_id.id','=',user_id),('expiry_date','>=',now)])
            for record in records:
                if product.id in record.product_ids._ids:
                    subscription = True
                    break
        not_play = False
        if not subscription:
            if product.post_date < now:
                not_play = True
        partner_id = request.env.user.partner_id.id
        downloaded_product = request.env['jkv.download'].sudo().search([('product_id.id', '=', product.id), ('partner_id.id', '=', partner_id),
                                                                       ('downloaded', '=', True)], limit=1)
        not_play = False if downloaded_product else not_play
        res.qcontext.update({'subscription': subscription, 'not_play': not_play, 'free_view': False})
        return res

    @http.route()
    def cart(self, **post):
        res = super(WebsiteSaleExt, self).cart(**post)
        # Update url for Continue button:
        if request.session.get('filter_url', False):
            res.qcontext.update({'filter_url': request.session['filter_url']})
        return res

    @http.route(['/shop/uid'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def get_uid(self):
        return {'uid': request.session.uid}
