from operator import itemgetter
from itertools import groupby
import json
import werkzeug

from odoo import http, _
from odoo.addons.web.controllers.main import ensure_db, Home
from odoo.addons.website_portal.controllers.main import website_account
from odoo.addons.jkv_website_purchase.controllers.main import WebsitePurchase
from odoo.http import request
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website_sale.controllers.main import TableCompute, PPG , PPR , WebsiteSale
from odoo.addons.jkv_signup.controllers.main import SUPPORTED_COUNTRY_CODES
from odoo.addons.jkv_website_sale.controllers.main import WebsiteSaleExt
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime
from odoo.addons.auth_signup.models.res_users import SignupError
from ..utils.akamai_token_v2 import AkamaiToken, AkamaiTokenError

import logging
_logger = logging.getLogger(__name__)


class Website(Home):

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, *args, **kw):
        """
            Load list of states to implement sign up view
        """
        call_to_action = request.env['jkv.calltoaction'].search(
            [('id', '=', request.env.ref("jkv_theme.signup_login").id)]).status
        response = super(Website, self).web_login(redirect=redirect, *args, **kw)
        countries = request.env['res.country'].sudo().search([('code', 'in', SUPPORTED_COUNTRY_CODES)])
        states = request.env['res.country.state'].sudo().search(
            [('country_id.id', 'in', countries.ids)]
        )
        response.qcontext.update({'states': states, 'countries': countries, 'call_to_action': call_to_action})
        if request.httprequest.method == 'GET':
            response.qcontext.update(first_load=True)
        if request.params.get('login_success', False) and kw.get('productId', False):
            sale_order = request.env['website'].browse(request.website.id).sale_get_order(force_create=True)
            if sale_order.state != 'draft':
                request.session['sale_order_id'] = None
                sale_order = request.env['website'].browse(request.website.id).sale_get_order(force_create=True)
            sale_order._cart_update(
                product_id=int(kw.get('productId', False))
            )
        return response

    @http.route('/page/<page:page>', type='http', auth="public", website=True, cache=300)
    def page(self, page, **opt):
        response = super(Website, self).page(page, **opt)
        if page == 'homepage':
            # Load 3 latest products to Home page
            keep = QueryURL('/search_videos/results')
            products = request.env['product.template'].sudo().search([], limit=3, order='id desc')
            live_stream = request.env['jkv.livestream'].sudo().search([('live_now', '=', True)], limit=1)
            call_to_action = request.env['jkv.calltoaction'].search([('id','=', request.env.ref("jkv_theme.home").id)]).status
            response.qcontext.update({'products': products, 'keep': keep,
                                      'title_livestream': live_stream.title,
                                      'live_now': live_stream.live_now,
                                      'call_to_action': call_to_action})

        return response

    @http.route('/web/signup', type='http', auth='public', website=True)
    def web_auth_signup(self, *args, **kw):
        request.params['name'] = "{} {}".format(request.params.get('jkv_first_name'), request.params.get('jkv_last_name'))
        response = super(Website, self).web_auth_signup(*args, **kw)
        call_to_action = request.env['jkv.calltoaction'].search(
            [('id', '=', request.env.ref("jkv_theme.signup_login").id)]).status
        if 'error' in response.qcontext:
            error_message = response.qcontext['error']
            del response.qcontext['error']
            response.qcontext.update({'signup_error': error_message, 'call_to_action': call_to_action})
        return response

    @http.route('/web/reset_password', type='http', auth='public', website=True)
    def web_auth_reset_password(self, *args, **kw):
        response = super(Website, self).web_auth_reset_password(*args, **kw)
        if '/my/home' in response.data:
            return response
        return request.render('jkv_theme.jkv_reset_password', response.qcontext)

    @http.route('/web/reset_username', type='http', auth='public', website=True)
    def web_auth_reset_username(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()
        if not qcontext.get('token') and not request.env['ir.config_parameter'].sudo().get_param('auth_signup.reset_username') == 'True':
            raise werkzeug.exceptions.NotFound()
        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                if qcontext.get('token'):
                    qcontext.update(self.do_update_username(qcontext))
                else:
                    login = qcontext.get('login')
                    assert login, "No login provided."
                    _logger.info(
                        "Username reset attempt for <%s> by user <%s> from %s",
                        login, request.env.user.login, request.httprequest.remote_addr)
                    request.env['res.users'].sudo().with_context(signup_force_type_in_url='reset_username').reset_username(login)
                    qcontext['message'] = _("An email has been sent with credentials to reset your username")
            except SignupError:
                qcontext['error'] = _("Could not reset your username")
                _logger.exception('error when resetting username')
            except Exception, e:
                qcontext['error'] = e.message or e.name
        if qcontext.get('isSuccess', False):
            return werkzeug.utils.redirect('/web/login')
        return request.render('jkv_theme.jkv_reset_username', qcontext)

    def do_update_username(self, qcontext):
        res = {}
        if qcontext.get('login', False) != qcontext.get('confirm_login', False):
            res['error'] = 'THE CONFIRMED USERNAME MUST BE THE SAME AS THE USERNAME!!'
        elif request.env['res.users'].search([('login','=',qcontext.get('login'))], limit=1):
            res['error'] = 'Username "%s" already exist, please try another!'%(qcontext.get('login'))
        if len(res) == 0:
            if qcontext.get('token'):
                partner = request.env['res.partner'].search([('signup_token', '=', qcontext.get('token'))], limit=1)
                partner.sudo().write({'signup_token': False, 'signup_type': False, 'signup_expiration': False})
                request.env['res.users'].search([('partner_id','=',partner.id)], limit=1).sudo().write({'login':qcontext.get('login')})
                res['isSuccess'] = True
            else:
                res['error'] = 'Invalid Token'
        return res



class WebsiteAccount(website_account):

    MANDATORY_BILLING_FIELDS = ["name", "phone", "email", "street", "city", "country_id", "jkv_first_name",
                                "jkv_last_name"]

    @http.route(['/page/contactus'], type='http', auth='public', website=True)
    def contactus(self):
        call_to_action = request.env['jkv.calltoaction'].search(
            [('id', '=', request.env.ref("jkv_theme.contact").id)]).status
        values = {
            'call_to_action': call_to_action,
        }
        return request.render("jkv_theme.jkv_theme_contactus", values)

    @http.route(['/page/thank'], type='http', auth='public', website=True)
    def thank(self):
        call_to_action = request.env['jkv.calltoaction'].search(
            [('id', '=', request.env.ref("jkv_theme.jk_thank").id)]).status
        values = {
            'call_to_action': call_to_action,
        }
        return request.render("jkv_theme.jkv_contact_thanks_inherit", values)

    @http.route(['/my', '/my/home'], type='http', auth="user", website=True)
    def account(self, **kw):
        response = super(WebsiteAccount, self).account(**kw)
        call_to_action = request.env['jkv.calltoaction'].search(
            [('id', '=', request.env.ref("jkv_theme.my_account").id)]).status
        # get videos
        user = request.env.user
        download = request.env['jkv.download']
        domain = [('partner_id.id', '=', user.partner_id.id)]
        videos = download.sudo().search(domain, order='create_date desc')
        response.qcontext.update({'videos': videos})

        # get subscriptions
        uid = request.session.uid
        subscription = request.env['jkv.subscription']
        domain = [('user_id.id', '=', uid)]
        subscriptions = subscription.sudo().search(domain)

        livestream_subscription = request.env['jkv.livestream.subscription'].sudo().search([('user_id', '=', uid)], limit=1)

        response.qcontext.update({
            'subscriptions': subscriptions,
            'livestream_subscription': livestream_subscription,
            'is_subscription': False,
            'is_livestream_subscription': False,
            'call_to_action': call_to_action
        })
        return response

    @http.route(['/my/subscriptions', '/my/subscriptions/page/<int:page>'], type='http', auth="user", website=True)
    def my_subscriptions(self, page=1, **kw):
        response = super(WebsiteAccount, self).my_subscriptions(page, **kw)

        # get videos
        user = request.env.user
        download = request.env['jkv.download']
        domain = [('partner_id.id', '=', user.partner_id.id)]
        videos = download.sudo().search(domain)
        response.qcontext.update({'videos': videos, 'is_subscription': True})
        return response

    @http.route(['/my/account'], type='http', auth='user', website=True)
    def details(self, redirect=None, **post):
        if post:
            post.update({'receive_email': 'receive_email' in post})

        call_to_action = request.env['jkv.calltoaction'].search(
            [('id', '=', request.env.ref("jkv_theme.contact_details").id)]).status

        countries = request.env['res.country'].sudo().search([('code', 'in', SUPPORTED_COUNTRY_CODES)])
        states = request.env['res.country.state'].sudo().search(
            [('country_id.id', 'in', countries.ids)]
        )
        response = super(WebsiteAccount, self).details(redirect=redirect, **post)
        response.qcontext.update({
            'states': states,
            'countries': countries,
            'username': request.env.user.login,
            'call_to_action': call_to_action
        })
        return response

    @http.route(['/services'], type='http', auth='public', website=True)
    def services(self):
        call_to_action = request.env['jkv.calltoaction'].search(
            [('id', '=', request.env.ref("jkv_theme.services").id)]).status
        values = {
            'call_to_action': call_to_action,
        }
        return request.render("jkv_theme.jkv_service_view", values)

    @http.route(['/service/jk-ringside'], type='http', auth='public', website=True)
    def jk_ringside(self):
        call_to_action = request.env['jkv.calltoaction'].search(
            [('id', '=', request.env.ref("jkv_theme.jk_ringside").id)]).status
        values = {
            'call_to_action': call_to_action,
        }
        return request.render("jkv_theme.jk_ringside_view", values)

    @http.route(['/service/jk-download'], type='http', auth='public', website=True)
    def jk_download(self):
        call_to_action = request.env['jkv.calltoaction'].search(
            [('id', '=', request.env.ref("jkv_theme.jk_download").id)]).status
        values = {
            'call_to_action': call_to_action,
        }
        return request.render("jkv_theme.jk_download_view", values)

    @http.route(['/service/jk-stream'], type='http', auth='public', website=True)
    def jk_stream(self):
        call_to_action = request.env['jkv.calltoaction'].search(
            [('id', '=', request.env.ref("jkv_theme.jk_stream").id)]).status
        values = {
            'call_to_action': call_to_action,
        }
        return request.render("jkv_theme.jk_stream_view", values)

    @http.route(['/page/live-video-main'], type='http', auth='public', website=True)
    def videos_main(self, redirect=None, **post):
        keep = QueryURL('/search_videos/results')
        products = request.env['product.template'].sudo().search([], limit=3, order='id desc')
        live_stream = request.env['jkv.livestream'].sudo().search([], limit=1)
        call_to_action = request.env['jkv.calltoaction'].search(
            [('id', '=', request.env.ref("jkv_theme.live_stream").id)]).status
        values = {
            'products': products,
            'keep': keep,
            'title_livestream': live_stream.title,
            'license': live_stream.license,
            'source_url': live_stream.source_url,
            'call_to_action': call_to_action
        }
        return request.render("jkv_theme.jkv_videos", values)

    def _generate_livestream_token(self, secret_key):
        # Generate livestream token
        new_token = ''
        try:
            generator = AkamaiToken(
                window_seconds=request.env.ref('jkv_theme.jkv_livestream_token_valid_time').value,
                acl='/*',
                key=secret_key,
            )
            new_token = generator.generateToken()
        except AkamaiTokenError, ex:
            _logger.error(ex)
        except Exception, ex:
            _logger.error(ex)

        return new_token

    @http.route(['/page/livestream-main'], type='http', auth='user', website=True)
    def livestream_main(self, redirect=None, **post):
        keep = QueryURL('/search_videos/results')
        products = request.env['product.template'].sudo().search([], limit=3, order='id desc')
        live_stream = request.env.ref('jkv_theme.jkv_livestream_data')
        call_to_action = request.env['jkv.calltoaction'].search(
            [('id', '=', request.env.ref("jkv_theme.live_stream").id)]).status
        jkv_livestream_security = request.env.ref('jkv_theme.jkv_livestream_security').value
        livestream_security = jkv_livestream_security == '1' and True or False

        livestream_subscription = request.env['jkv.livestream.subscription'].sudo().search(
            [('user_id.id', '=', request.session.uid)], limit=1)
        if not livestream_subscription or livestream_subscription.is_expired:
            values = {
                'products': products,
                'keep': keep,
                'title_livestream': '',
                'license': '',
                'source_url': '',
                'call_to_action': call_to_action,
                'no_subscription': True
            }
            return request.render("jkv_theme.jkv_live_steam", values)

        # Generate livestream url
        secret_key = request.env.ref('jkv_theme.jkv_livestream_secret_key').value
        new_token = self._generate_livestream_token(secret_key)

        values = {
            'products': products,
            'keep': keep,
            'title_livestream': live_stream.title,
            'license': live_stream.license,
            'source_url': livestream_security and '{}?{}'.format(live_stream.source_url, new_token) or live_stream.source_url,
            'call_to_action': call_to_action,
            'livestream_security': livestream_security,
            'query_param': new_token and new_token[6:]
        }
        return request.render("jkv_theme.jkv_live_steam", values)

    @http.route(['/page/livestream-tellespen'], type='http', auth='user', website=True)
    def livestream_tellespen(self, redirect=None, **post):
        keep = QueryURL('/search_videos/results')
        products = request.env['product.template'].sudo().search([], limit=3, order='id desc')
        live_stream = request.env.ref('jkv_theme.jkv_livestream_tellespen_data')
        call_to_action = request.env['jkv.calltoaction'].search(
            [('id', '=', request.env.ref("jkv_theme.live_stream").id)]).status
        jkv_livestream_security = request.env.ref('jkv_theme.jkv_livestream_security').value
        livestream_security = jkv_livestream_security == '1' and True or False

        livestream_subscription = request.env['jkv.livestream.subscription'].sudo().search(
            [('user_id.id', '=', request.session.uid)], limit=1)
        if not livestream_subscription or livestream_subscription.is_expired:
            values = {
                'products': products,
                'keep': keep,
                'title_livestream': '',
                'license': '',
                'source_url': '',
                'call_to_action': call_to_action,
                'no_subscription': True
            }
            return request.render("jkv_theme.jkv_live_steam", values)

        # Generate livestream url
        secret_key = request.env.ref('jkv_theme.jkv_livestream_secret_key_tellespen').value
        new_token = self._generate_livestream_token(secret_key)

        values = {
            'products': products,
            'keep': keep,
            'title_livestream': live_stream.title,
            'license': live_stream.license,
            'source_url': livestream_security and '{}?{}'.format(live_stream.source_url, new_token) or live_stream.source_url,
            'call_to_action': call_to_action,
            'livestream_security': livestream_security,
            'query_param': new_token and new_token[6:]
        }
        return request.render("jkv_theme.jkv_live_steam", values)

    @http.route(['/page/pricing'], type='http', auth='public', website=True)
    def pricing(self, redirect=None, **post):
        keep = QueryURL('/search_videos/results')
        products = request.env['product.template'].sudo().search([], limit=3, order='id desc')
        call_to_action = request.env['jkv.calltoaction'].search(
            [('id', '=', request.env.ref("jkv_theme.pricing").id)]).status
        values = {
            'products': products,
            'keep': keep,
            'call_to_action': call_to_action,
            'livestream_subscription_price': request.env.ref('jkv_website_purchase.subscription_livestream').value
        }
        return request.render("jkv_theme.jkv_pricing", values)

    @http.route(['/page/terms'], type='http', auth='public', website=True)
    def terms(self, redirect=None, **post):
        return request.render("jkv_theme.jkv_terms")

    @http.route(["/page/privacy"], type='http', auth='public', website=True)
    def privacy(self, redirect=None, **post):
        return request.render("jkv_theme.jkv_privacy")


class WebsitePurchase(WebsitePurchase):

    @http.route(['/purchase_subscription'], type='http', auth="user", website=True)
    def purchase_subscription(self, **args):
        response = super(WebsitePurchase, self).purchase_subscription(**args)
        call_to_action = request.env['jkv.calltoaction'].search([('id', '=', request.env.ref("jkv_theme.purchase_subscription").id)]).status
        order = request.website.sale_get_order()
        order = False if order is None else order

        all_show = []
        partner_show = []
        show_records = request.env['jkv.show.venue'].sudo().search([])
        subscription_data = request.env['jkv.subscription'].sudo().search([('expiried', '=', True), ('user_id.id', '=', request.session.uid)])
        show_subscribed = [u.show_id.id for u in subscription_data]

        # All show
        for show in show_records:
            if show.id not in show_subscribed:
                all_show.append(show)
        # Partner show
        for show in request.env.user.partner_id.show_ids:
            if show.id not in show_subscribed:
                partner_show.append(show)

        is_livestream_subscription = args.get('is_livestream_subscription', False)

        response.qcontext.update({'all_show': all_show, 'partner_show': partner_show, 'order': order, 'call_to_action': call_to_action, 'is_livestream_subscription': is_livestream_subscription})
        return response

    @http.route('/filter_shows', type='json', auth='user', method="post")
    def filter_shows(self, filter_string, type_video):

        result = ({'type_video': type_video, 'shows': []})
        subscription_data = request.env['jkv.subscription'].sudo().search([('expiried', '=', True),('user_id.id', '=', request.session.uid)])
        show_subscribed = [u.show_id.id for u in subscription_data]

        if type_video == "all_videos":
            # All show
            show_records = request.env['jkv.show.venue'].sudo().search([])
        else:
            # Partner show
            show_records = request.env.user.partner_id.show_ids

        show_filtered = []
        for show in show_records:
            if show.id not in show_subscribed and show.name.lower().find(filter_string) != -1:
                show_filtered.append({'id': show.id, 'name': show.name})

        result.update({'shows': show_filtered})
        return result


class JKVWebsiteSaleExt(WebsiteSaleExt):
    @http.route(['/blogs'], type='http', auth='public', website=True)
    def blog(self, page=0, category=None, search='', ppg=False, website=True, **kwargs):
        ppg = 5
        blog_archive = request.env['jkv.blog'].sudo().search_read([], ['blog_archive'], order='blog_date DESC')
        blog_archive_view = []
        for temp in blog_archive:
            if temp['blog_archive'] not in blog_archive_view:
                blog_archive_view.append(temp['blog_archive'])
        jkv_blogs = request.env['jkv.blog'].sudo().search([], order='blog_date desc')
        if jkv_blogs:
            first_jkv_blog = jkv_blogs[0]
        else:
            first_jkv_blog = []
        keep = QueryURL('/blogs')

        url = "/search_article/results"
        pager = self._pager(url=url, total=len(jkv_blogs), page=page, step=ppg, scope=7, url_args=keep(url))
        domain = []
        jkv_blogs = request.env['jkv.blog'].sudo().search(domain, order='blog_date desc', limit=(ppg - 1),
                                                          offset=pager['offset'])
        jkv_blogs = jkv_blogs[1:]
        jkv_tags = request.env['jkv.tag'].sudo().search_read([], ['name'], order='name desc')
        call_to_action = request.env['jkv.calltoaction'].search(
            [('id', '=', request.env.ref("jkv_theme.blog").id)]).status
        values = {
            'first_blog': first_jkv_blog,
            'blogs': jkv_blogs,
            'tags': jkv_tags,
            'archives': blog_archive_view,
            'keep': keep,
            'pager': pager,
            'call_to_action': call_to_action,
        }
        return request.render("jkv_theme.jkv_blog", values)

    def _format_blog_archive(self, date):
        month_switcher = {
            'JANUARY': '01',
            'FEBRUARY': '02',
            'MARCH': '03',
            'APRIL': '04',
            'MAY': '05',
            'JUNE': '06',
            'JULY': '07',
            'AUGUST': '08',
            'SEPTEMBER': '09',
            'OCTOBER': '10',
            'NOVEMBER': '11',
            'DECEMBER': '12',
        }
        month = month_switcher.get(date.split(" ")[0], "Invalid month of years")
        return date.split(" ")[1] + "-" + month

    @http.route([
        '/search_article/results',
        '/search_article/results/page/<int:page>'
    ], type='http', auth="public", website=True)
    def jkv_search_article(self, page=0, category=None, search='', ppg=False, website=True, **kwargs):
        ppg = 5
        domain = []
        request.session['filter_url'] = request.httprequest.url
        blog_archives_selected = request.httprequest.args.getlist('blog_archive')
        blog_tags_selected = request.httprequest.args.getlist('blog_tag')
        blog_tags = request.env['jkv.tag'].sudo().search_read([], ['name'], order='name desc')
        blog_archive = request.env['jkv.blog'].sudo().search_read([], ['blog_archive'], order='blog_date DESC')
        blog_archive_view = []
        for temp in blog_archive:
            if temp['blog_archive'] not in blog_archive_view:
                blog_archive_view.append(temp['blog_archive'])
        tag_ids = request.env['jkv.tag'].sudo().search_read([], ['id', 'name'], order='name DESC')
        url = "/search_article/results"
        keep = QueryURL('/search_article/results', search=search, attrib=[],
                        order=kwargs.get('order'),
                        blog_archive=blog_archives_selected, blog_tag=blog_tags_selected)
        if blog_archives_selected:
            for i in range(len(blog_archives_selected) - 1):
                domain += ['|', ]
            for i in range(len(blog_archives_selected)):
                domain += [('blog_date', 'ilike', self._format_blog_archive(blog_archives_selected[i]))]

        blog_tags_ids = list(map(lambda id: int(id), blog_tags_selected))
        blog_tags_selected = list(filter(lambda tag: tag['id'] in blog_tags_ids, tag_ids))
        if blog_tags_selected:
            domain.append(('blog_tags.id', 'in', blog_tags_ids))

        jkv_blogs = request.env['jkv.blog'].sudo().search(domain)
        pager = self._pager(url=url, total=len(jkv_blogs), page=page, step=ppg, scope=7, url_args=keep(url))
        jkv_blogs = request.env['jkv.blog'].sudo().search(domain, limit=ppg, offset=pager['offset'])
        if jkv_blogs:
            first_jkv_blog = jkv_blogs[0]
        else:
            first_jkv_blog = []
        jkv_blogs = jkv_blogs[1:]
        call_to_action = request.env['jkv.calltoaction'].search(
            [('id', '=', request.env.ref("jkv_theme.blog").id)]).status
        values = {
            'first_blog': first_jkv_blog,
            'blogs': jkv_blogs,
            'tags': blog_tags,
            'blog_tags_selected': blog_tags_selected,
            'archives': blog_archive_view,
            'blog_archive_selected': blog_archives_selected,
            'keep': keep,
            'pager': pager,
            'call_to_action': call_to_action,
        }
        return request.render("jkv_theme.jkv_blog", values)

    @http.route(['/blog/article/<model("jkv.blog"):article>'], type='http', auth="public", website=True)
    def article(self, article, redirect=None, **kwargs):
        blog_tags = request.env['jkv.tag'].sudo().search_read([], ['name'], order='name desc')
        blog_archive = request.env['jkv.blog'].sudo().search_read([], ['blog_archive'], order='blog_date DESC')
        blog_archive_view = []
        for temp in blog_archive:
            if temp['blog_archive'] not in blog_archive_view:
                blog_archive_view.append(temp['blog_archive'])
        domain = ()
        next_blog = []
        previous_blog = []
        if article:
            jkv_article = request.env['jkv.blog'].sudo().search([('id', '=', article.id)], limit=1)

        keep = QueryURL('/blog/article')
        blog_tags_selected = jkv_article.blog_tags
        blog_tags_ids = list(map(lambda id: int(id), blog_tags_selected))
        if blog_tags_ids:
            domain = ('blog_tags.id', 'in', blog_tags_ids)
            next_blog = request.env['jkv.blog'].sudo().search([domain, ('blog_date', '>', jkv_article.blog_date)],
                                                            order='blog_date', limit=1)
            previous_blog = request.env['jkv.blog'].sudo().search([domain, ('blog_date', '<', jkv_article.blog_date)],
                                                                order='blog_date desc', limit=1)
        call_to_action = request.env['jkv.calltoaction'].search(
            [('id', '=', request.env.ref("jkv_theme.article").id)]).status
        values = {
            'jkv_article': jkv_article,
            'previous_blog': previous_blog,
            'next_blog': next_blog,
            'blog_archive': blog_archive_view,
            'blog_tags': blog_tags,
            'keep': keep,
            'blog_tags_ids': blog_tags_ids,
            'blog_tags_selected': blog_tags_selected,
            'call_to_action': call_to_action,
        }
        return request.render("jkv_theme.jkv_article", values)

    # Deprecated route: /search_videos
    # Override and Overwrite in order to remove this url from website
    def jkv_search_template(self, **kwargs):
        pass

    @http.route([
        '/search_videos/results',
        '/search_videos/results/page/<int:page>'
    ], type='http', auth="public", website=True)
    def jkv_search_videos_feature(self, page=0, category=None, search='', ppg=False, website=True, **kwargs):
        # Update url for Continue button:
        request.session['filter_url'] = request.httprequest.url
        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = PPG
        else:
            ppg = PPG

        is_livestream_product = bool(request.httprequest.args.get('is_livestream_product', False))
        show_numbers = request.httprequest.args.getlist('show_number')
        class_numbers = request.httprequest.args.getlist('class_number')
        livestream_show_numbers = request.httprequest.args.getlist('livestream_show_number')
        livestream_class_numbers = request.httprequest.args.getlist('livestream_class_number')
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
        # Changes 03/05/18
        show_my_videos = request.httprequest.args.get('show_my_videos')

        jkv_collapse = request.httprequest.args.get('jkv_collapse', 'collapse2')
        if is_livestream_product:
            keep = QueryURL('/search_videos/results', category=category and int(category), search=search, attrib=[],
                            order=kwargs.get('order'),
                            livestream_show_number=livestream_show_numbers, livestream_class_number=livestream_class_numbers,
                            jkv_start_date_search_video=jkv_start_date_search_video,
                            jkv_end_date_search_video=jkv_end_date_search_video,
                            show_all_video=show_all_video, subscribed_video_only=subscribed_video_only,
                            jkv_collapse=jkv_collapse, is_livestream_product=is_livestream_product)
        else:
            keep = QueryURL('/search_videos/results', category=category and int(category), search=search, attrib=[],
                            order=kwargs.get('order'),
                            show_number=show_numbers, class_number=class_numbers, rider_name=rider_names,
                            rider_number=rider_numbers, post_day=post_days,
                            horse_name=horse_names, ride_number=ride_numbers,
                            jkv_start_date_search_video=jkv_start_date_search_video,
                            jkv_end_date_search_video=jkv_end_date_search_video,
                            show_all_video=show_all_video, subscribed_video_only=subscribed_video_only,
                            jkv_collapse=jkv_collapse)

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
        if is_livestream_product:
            livestream_show_numbers = list(map(lambda id: int(id), livestream_show_numbers))
            livestream_class_numbers = list(map(lambda id: int(id), livestream_class_numbers))
            values = {
                'post_checked_days': post_days,
                'jkv_collapse': jkv_collapse,
                'livestream_show_checked_ids': livestream_show_numbers,
                'livestream_class_checked_ids': livestream_class_numbers
            }
        else:
            show_numbers = list(map(lambda id: int(id), show_numbers))
            class_numbers = list(map(lambda id: int(id), class_numbers))
            values = {
                'rider_checked_names': rider_names,
                'rider_checked_numbers': rider_numbers,
                'post_checked_days': post_days,
                'horse_checked_names': horse_names,
                'jkv_collapse': jkv_collapse,
                'show_checked_ids': show_numbers,
                'class_checked_ids': class_numbers
            }

        user_id = request.session.uid
        user = request.env['res.users'].sudo().search([('id', '=', user_id)])
        partner = user.partner_id

        subscriptions = request.env['jkv.subscription'].sudo().search(
            [('user_id.id', '=', user_id), ('expiried', '=', False)], order='expiry_date DESC')
        subscription_status = {}
        product_subcribed_no_expire = []
        for subscription in subscriptions:
            for product in subscription.product_ids:
                product_subcribed_no_expire.append(product)
                if product.id not in subscription_status:
                    subscription_status[product.id] = subscription

        values.update({
            'subscriptions': subscriptions,
            'subscription_status': subscription_status,
            'product_subcribed_no_expire': product_subcribed_no_expire,
        })

        # Remove all shows
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
        if not is_livestream_product:
            domain.append(('filename_id', '!=', False))
        if jkv_start_date_search_video:
            domain.append(('filename_id.show_id.end_date', '>=', jkv_start_date_search_video))
        if jkv_end_date_search_video:
            domain.append(('filename_id.show_id.start_date', '<=', jkv_end_date_search_video))
        # GET VIDEO WHICH SEARCHED IN FORM BEFORE, BY DATE AND USER

        if show_all_video:
            values.update({'show_all_video': show_all_video})
        if subscribed_video_only:
            values.update({'subscribed_video_only': subscribed_video_only})

        # Changes 03/05/18
        if show_my_videos:
            values.update({'show_my_videos': show_my_videos})

        if subscribed_video_only:
            subscriptions = request.env['jkv.subscription'].sudo().search([('user_id.id', '=', user_id)])
            videos_subcribed = []
            for subscription in subscriptions:
                if subscription.product_ids:
                    videos_subcribed = videos_subcribed + list(subscription.product_ids._ids)
            domain.append(('id', 'in', videos_subcribed))
        elif not subscribed_video_only and show_my_videos:  # Changes 03/05/18 elif not subscribed_video_only and not show_all_video
            domain.append(('id', 'in', partner.mapping_videos._ids))

        if not show_my_videos and not subscribed_video_only:
            show_all_video = True

        """
            Do a search when users put something on the search bar
        """
        if search:
            for srch in search.split(" "):
                domain += [
                    '|', '|', '|', '|', ('filename_id.show_id.name', 'ilike', srch),
                    ('filename_id.class_id.name', 'ilike', srch),
                    ('rider_name', 'ilike', srch),
                    ('rider_number', 'ilike', srch), ('horse_name', 'ilike', srch)]

        # IF USER CHOOSE VIEW THE LAST FILTER
        if jkv_view_last_filter:
            domain = [('id', 'in', partner.jkv_last_filter_video_ids._ids)]
            products = partner.jkv_last_filter_video_ids

        # IF USER CHOSE CREATE A NEW FILTER
        # CREATE DOMAIN FOR SEARCHING
        else:
            if show_numbers:
                domain.append(('filename_id.show_id.id', 'in', show_numbers))
            if class_numbers:
                domain.append(('filename_id.class_id.id', 'in', class_numbers))
            if livestream_show_numbers:
                domain.append(('livestream_show_id.id', 'in', livestream_show_numbers))
            if livestream_class_numbers:
                domain.append(('livestream_class_id.id', 'in', livestream_class_numbers))
            if is_livestream_product:
                domain.append(('is_livestream_product', '=', is_livestream_product))
            if rider_names:
                domain.append('|')
                domain.append(('filename_id.rider_id.rider_id.name', 'in', rider_names))
                domain.append(('filename_id.rider_id.rider_2nd_id.name', 'in', rider_names))
            if rider_numbers:
                domain.append(('rider_number', 'in', rider_numbers))
            if horse_names:
                domain.append(('horse_name', 'in', horse_names))
            if post_days:
                domain.append(('post_day', 'in', post_days))

            products = request.env['product.template'].sudo().search(domain)

            if partner:
                if jkv_save_filter:
                    partner.write({'jkv_save_filter': True})
                    list_jkv_last_filter_videos = []
                    for product in products:
                        list_jkv_last_filter_videos.append(product.id)
                    partner.jkv_last_filter_video_ids = [(6, 0, list_jkv_last_filter_videos)]
                else:
                    partner.write({'jkv_save_filter': False})

        pricelist_context = dict(request.env.context)
        if not pricelist_context.get('pricelist'):
            pricelist = request.website.get_current_pricelist()
            pricelist_context['pricelist'] = pricelist.id
        else:
            pricelist = request.env['product.pricelist'].browse(pricelist_context['pricelist'])

        request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)
        data_rider_ids = []
        if is_livestream_product:
            livestream_show_ids = request.env['jkv_livestream.show'].sudo().search_read([], ['id', 'name', 'show_number'],
                                                                        order='start_date DESC')
            livestream_selected_shows = list(filter(lambda livestream_show: livestream_show['id'] in livestream_show_numbers, livestream_show_ids))

            livestream_selected_show_objs = request.env['jkv_livestream.show'].browse(livestream_show_numbers)
            # data_livestream_class_ids = []
            # for u in livestream_selected_show_objs:
            #     data_livestream_class_ids.extend(u.class_ids._ids)
            #     data_rider_ids.extend(u.rider_ids._ids)

            # livestream_class_ids = []
            if products:
                livestream_class_ids = request.env['jkv_livestream.class'].sudo().search_read(
                    [('id', 'in', [u.livestream_class_id.id for u in products])], ['id', 'name', 'class_number'],
                    order='name ASC')
            else:
                livestream_class_ids = request.env['jkv_livestream.class'].sudo().search_read([],
                                                                        ['id', 'name', 'class_number'],
                                                                        order='name ASC')
            livestream_selected_classes = list(filter(lambda livestream_class_number: livestream_class_number['id'] in livestream_class_numbers, livestream_class_ids))
        else:
            show_ids = request.env['jkv.show.venue'].sudo().search_read([], ['id', 'name', 'show_number'],
                                                                        order='start_date DESC')
            selected_shows = list(filter(lambda show: show['id'] in show_numbers, show_ids))

            selected_show_objs = request.env['jkv.show.venue'].browse(show_numbers)
            data_class_ids = []
            for u in selected_show_objs:
                data_class_ids.extend(u.class_ids._ids)
                data_rider_ids.extend(u.rider_ids._ids)

            class_ids = []
            if data_class_ids:
                class_ids = request.env['jkv.class'].sudo().search_read([('id', 'in', data_class_ids)],
                                                                        ['id', 'name', 'class_number'], order='name ASC')
            else:
                class_ids = request.env['jkv.class'].sudo().search_read([],
                                                                        ['id', 'name', 'class_number'], order='name ASC')
            selected_classes = list(filter(lambda class_number: class_number['id'] in class_numbers, class_ids))

        # DATA FOR LEFT PART OF PAGE RESULT
        if not is_livestream_product:
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
        if is_livestream_product:
            values.update({
                'livestream_show_ids': livestream_show_ids,
                'livestream_class_ids': livestream_class_ids,
                # 'rider_names': list_rider_names,
                # 'rider_numbers': list_rider_numbers,
                'post_days': list_post_days_filter,
                # 'horse_names': list_horse_names,
                'jkv_start_date_search_video': jkv_start_date_search_video,
                'jkv_end_date_search_video': jkv_end_date_search_video,
                'livestream_selected_shows': livestream_selected_shows,
                'livestream_selected_classes': livestream_selected_classes,
                'is_livestream_product': is_livestream_product
            })
        else:
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
                'selected_classes': selected_classes,
                'is_livestream_product': is_livestream_product
            })

        url = "/search_videos/results"
        # pager = request.website.pager(url=url, total=len(products), page=page, step=PPG, scope=7, url_args=kwargs)
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
        downloads = request.env['jkv.download'].sudo().search(
            [('product_id.id', 'in', products._ids), ('partner_id.id', '=', partner_id)])
        products_purchased = []
        download_url = {}
        for download in downloads:
            products_purchased.append(download.product_id)
            download_url[download.product_id.id] = request.httprequest.url_root + 'thank_you?token=' + download.token

        all_products_purchased = request.env['jkv.download'].sudo().search(
            [('product_id.id', 'in', products._ids), ('partner_id.id', '=', partner_id)])
        share_link_prefix = '{}shop/product/'.format(request.httprequest.host_url)
        call_to_action = request.env['jkv.calltoaction'].search(
            [('id', '=', request.env.ref("jkv_theme.video_archive").id)]).status
        values.update({
            'products_purchased': products_purchased,
            'download_url': download_url,
            'all_products_purchased': [p.product_id for p in all_products_purchased],
            'share_link_prefix': share_link_prefix,
            'search': search,
            'call_to_action': call_to_action,
        })

        return request.render("website_sale.products", values)


class WebsiteSale(WebsiteSale):
    @http.route(['/shop/cart'], type='http', auth="public", website=True)
    def cart(self, **post):
        order = request.website.sale_get_order()
        if order:
            from_currency = order.company_id.currency_id
            to_currency = order.pricelist_id.currency_id
            compute_currency = lambda price: from_currency.compute(price, to_currency)
        else:
            compute_currency = lambda price: price
        call_to_action = request.env['jkv.calltoaction'].search(
            [('id', '=', request.env.ref("jkv_theme.payment_process").id)]).status
        values = {
            'website_sale_order': order,
            'compute_currency': compute_currency,
            'suggested_products': [],
            'call_to_action': call_to_action,
        }
        if order:
            _order = order
            if not request.env.context.get('pricelist'):
                _order = order.with_context(pricelist=order.pricelist_id.id)
            values['suggested_products'] = _order._cart_accessories()

        if post.get('type') == 'popover':
            # force no-cache so IE11 doesn't cache this XHR
            return request.render("website_sale.cart_popover", values, headers={'Cache-Control': 'no-cache'})

        if post.get('code_not_available'):
            values['code_not_available'] = post.get('code_not_available')

        return request.render("website_sale.cart", values)

    @http.route(['/shop/checkout'], type='http', auth="public", website=True)
    def checkout(self, **post):
        order = request.website.sale_get_order()
        call_to_action = request.env['jkv.calltoaction'].search(
            [('id', '=', request.env.ref("jkv_theme.payment_process").id)]).status
        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            return request.redirect('/shop/address')

        for f in self._get_mandatory_billing_fields():
            if not order.partner_id[f]:
                return request.redirect('/shop/address?partner_id=%d' % order.partner_id.id)
        values = self.checkout_values(**post)
        values.update({
            'call_to_action': call_to_action,
        })
        # Avoid useless rendering if called in ajax
        if post.get('xhr'):
            return 'ok'
        return request.render("website_sale.checkout", values)

    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product(self, product, category='', search='', **post):
        call_to_action = request.env['jkv.calltoaction'].search(
            [('id', '=', request.env.ref("jkv_theme.video_details").id)]).status
        response = super(WebsiteSale, self).product(product, **post)
        response.qcontext.update({'call_to_action': call_to_action})
        return response

    @http.route(['/shop/payment'], type='http', auth="public", website=True)
    def payment(self, **post):
        response = super(WebsiteSale, self).payment(**post)
        call_to_action = request.env['jkv.calltoaction'].search(
            [('id', '=', request.env.ref("jkv_theme.payment_process").id)]).status
        if 'website_sale_order' in response.qcontext:
            order = response.qcontext['website_sale_order']
            from_currency = order.company_id.currency_id
            to_currency = order.pricelist_id.currency_id
            compute_currency = lambda price: from_currency.compute(price, to_currency)
        else:
            compute_currency = lambda price: price

        response.qcontext.update({'compute_currency': compute_currency, 'call_to_action': call_to_action})
        return response

    @http.route(['/shop/confirmation'], type='http', auth="public", website=True)
    def payment_confirmation(self, **post):
        """ End of checkout process controller. Confirmation is basically seing
        the status of a sale.order. State at this point :

         - should not have any context / session info: clean them
         - take a sale.order id, because we request a sale.order and are not
           session dependant anymore
        """
        call_to_action = request.env['jkv.calltoaction'].search(
            [('id', '=', request.env.ref("jkv_theme.payment_process").id)]).status
        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            is_redirect = False
            redirect_url = False
            livestream_product_id = request.env.ref('jkv_website_purchase.product_livestream_subscription').id
            if order and any(product_id == livestream_product_id for product_id in order.order_line.mapped('product_id.id')):
                is_redirect = True
                # redirect_url = request.env['jkv.livestream'].search([('live_now', '=', True)], limit=1)
                redirect_url = '/page/live-video-main'
            return request.render("website_sale.confirmation", {'order': order, 'call_to_action': call_to_action, 'is_redirect': is_redirect, 'redirect_url': redirect_url if redirect_url else False})
        else:
            return request.redirect('/shop')

    @http.route([
        '/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>'
    ], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        call_to_action = request.env['jkv.calltoaction'].search(
            [('id', '=', request.env.ref("jkv_theme.video_archive").id)]).status
        response = super(WebsiteSale, self).shop(page=page,category=category,search=search, ppg=ppg,**post)
        response.qcontext.update({'video_active': True, 'call_to_action': call_to_action})
        return response


class WebsiteSaleExt(WebsiteSale):
    @http.route([
        '/page/events-calendar',
        '/page/events-calendar/page/<int:page>',
    ], type='http', auth="public", website=True)
    def calendar(self, page=0, **kwargs):
        ppg = 6
        domain = []
        url = "/page/events-calendar"
        now = datetime.now().date()
        currentyear = now.year
        events = request.env['jkv.events.calendar'].search(domain)
        pager = request.website.pager(url=url, total=len(events), page=page, step=ppg, scope=7, url_args=kwargs)
        events = request.env['jkv.events.calendar'].sudo().search(domain, limit=ppg, offset=pager['offset'],
                                                                  order='event_date desc')
        showcurrentyears = request.env['jkv.show.venue'].sudo().search_read(
            [('start_date', '<=', now.replace(month=12, day=31).strftime(DEFAULT_SERVER_DATE_FORMAT)),
             ('start_date', '>=', now.replace(month=1, day=1).strftime(DEFAULT_SERVER_DATE_FORMAT))],
            ['id', 'name', 'show_number'], order='start_date DESC')
        events_calendar = request.env['jkv.events.calendar'].sudo().search_read([], ['id', 'name', 'show_number',
                                                                                     'start_date', 'end_date',
                                                                                     'start_date_format',
                                                                                     'end_date_format', 'gsec_schedule',
                                                                                     'prize_list'], order='start_date ASC')
        call_to_action = request.env['jkv.calltoaction'].search(
                [('id', '=', request.env.ref("jkv_theme.calendar").id)]).status

        values = {
            'pager': pager,
            'events': events,
            'showcurrentyears': showcurrentyears,
            'shows': events_calendar,
            'currentyear': currentyear,
            'call_to_action': call_to_action,
        }
        return request.render("jkv_events_calendar.theme_events_calencar", values)

    @http.route([
        '/page/calendar',
    ], type='http', auth="public", website=True)
    def events_calendar(self, page=0, **kwargs):
        call_to_action = request.env['jkv.calltoaction'].search(
            [('id', '=', request.env.ref("jkv_theme.event_calendar").id)]).status
        values = {
            'call_to_action': call_to_action,
        }
        return request.render("jkv_theme.jkv_event_calendar", values)

    @http.route([
        '/page/livestream_calendar',
    ], type='http', auth="public", website=True)
    def events_livestream_calendar(self, page=0, **kwargs):
        call_to_action = request.env['jkv.calltoaction'].search(
            [('id', '=', request.env.ref("jkv_theme.event_livestream_calendar").id)]).status
        values = {
            'call_to_action': call_to_action,
        }
        return request.render("jkv_theme.jkv_event_livestream_calendar", values)

    @http.route(['/action_get_event_calendar'], type='json', auth="public")
    def action_get_event_calendar(self, **post):
        event_calendar_records = request.env['jkv.events.calendar'].sudo().search_read([], ['id', 'name', 'show_number',
                                                                                            'start_date', 'end_date',
                                                                                            'gsec_schedule',
                                                                                            'prize_list'])
        events = []
        for event in event_calendar_records:
            events.append({
                'title': event['name'].encode('ascii'),
                'start': event['start_date'],
                'end': event['end_date'],
                'url': '' if not event['gsec_schedule'] else event['gsec_schedule'].encode('ascii'),
                'allDay': True,
            })
        return events

    @http.route(['/action_get_event_livestream_calendar'], type='json', auth="public")
    def action_get_event_livestream_calendar(self, **post):
        event_livestream_calendar_records = request.env['jkv_livestream.show'].sudo().search_read([], ['id', 'name', 'show_number',
                                                                                            'start_date', 'end_date',
                                                                                            'page_url_id'])
        events = []
        for event in event_livestream_calendar_records:
            jkv_livestream = False
            event_dict = dict(event)
            if event_dict['page_url_id'] and len(event_dict['page_url_id']) > 1:
                jkv_livestream = request.env['jkv.livestream'].browse(event_dict['page_url_id'][0])
            events.append({
                'title': event['name'].encode('ascii'),
                'start': event['start_date'],
                'end': event['end_date'],
                'url': '' if not jkv_livestream else jkv_livestream.page_url,
                'allDay': True,
            })
        return events

