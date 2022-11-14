# -*- coding: utf-8 -*-
# Part of AppJetty. See LICENSE file for full copyright and
# licensing details.

import re
from odoo import http,SUPERUSER_ID
from odoo.http import request
from odoo.addons.website.models.website import slug
from odoo.addons.website_sale.controllers import main
from odoo.addons.website_sale.controllers import main as main_shop
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale.controllers.main import TableCompute


class ThemeFurnitoSliderSettings(http.Controller):

    @http.route(['/theme_furnito/pro_get_options'], type='json', auth="public", website=True)
    def get_slider_options(self):
        slider_options = []
        option = request.env['furnito.product.slider.config'].search(
            [('active', '=', True)], order="name asc")
        for record in option:
            slider_options.append({'id': record.id,
                                   'name': record.name})
        return slider_options

    @http.route(['/theme_furnito/pro_get_dynamic_slider'], type='http', auth='public', website=True)
    def get_dynamic_slider(self, **post):
        uid, context, pool = request.uid, dict(request.context), request.env
        if post.get('slider-type'):
            slider_header = request.env['furnito.product.slider.config'].sudo().search(
                [('id', '=', int(post.get('slider-type')))])

            if not context.get('pricelist'):
                pricelist = request.website.get_current_pricelist()
                context = dict(request.context, pricelist=int(pricelist))
            else:
                pricelist = pool.get('product.pricelist').browse(context['pricelist'])

            context.update({'pricelist': pricelist.id})

            from_currency = pool['res.users'].browse(uid).company_id.currency_id
            to_currency = pricelist.currency_id
            compute_currency = lambda price: pool['res.currency']._compute(from_currency, to_currency, price)
            for prod in slider_header.collections_product:
                prod.custom_snip_price = prod.website_price

            values = {
                'slider_header': slider_header,
                'slider_details': slider_header.collections_product,
                'compute_currency': compute_currency,
                }
            return request.render("theme_furnito.theme_furnito_pro_cat_slider_view", values)

    @http.route(['/theme_furnito/pro_image_effect_config'], type='json', auth='public', website=True)
    def product_image_dynamic_slider(self, **post):
        slider_data = request.env['furnito.product.slider.config'].search(
            [('id', '=', int(post.get('slider_type')))])
        values = {
            's_id': slider_data.id,
            'counts': slider_data.no_of_counts,
            'auto_rotate': slider_data.auto_rotate,
            'auto_play_time': slider_data.sliding_speed,
        }
        return values

    @http.route(['/theme_furnito/blog_get_options'], type='json', auth="public", website=True)
    def king_blog_get_slider_options(self):
        slider_options = []
        option = request.env['furnito.blog.slider.config'].search(
            [('active', '=', True)], order="name asc")
        for record in option:
            slider_options.append({'id': record.id,
                                   'name': record.name})
        return slider_options

    @http.route(['/theme_furnito/blog_get_dynamic_slider'], type='http', auth='public', website=True)
    def king_blog_get_dynamic_slider(self, **post):
        if post.get('slider-type'):
            slider_header = request.env['furnito.blog.slider.config'].sudo().search(
                [('id', '=', int(post.get('slider-type')))])

            values = {
                'slider_header': slider_header,
                'blog_slider_details': slider_header.collections_blog_post,
            }
            return request.render("theme_furnito.theme_furnito_blog_slider_view", values)

    @http.route(['/theme_furnito/blog_image_effect_config'], type='json', auth='public', website=True)
    def king_blog_product_image_dynamic_slider(self, **post):
        slider_data = request.env['furnito.blog.slider.config'].search(
            [('id', '=', int(post.get('slider_type')))])
        values = {
            's_id': slider_data.no_of_counts + '-' + str(slider_data.id),
            'counts': slider_data.no_of_counts,
            'auto_rotate': slider_data.auto_rotate,
            'auto_play_time': slider_data.sliding_speed,
        }
        return values

    # Multi image gallery
    @http.route(['/theme_furnito/multi_image_effect_config'], type='json', auth="public", website=True)
    def get_multi_image_effect_config(self):
        cur_website = request.website
        values = {
            'no_extra_options': cur_website.no_extra_options,
            'theme_panel_position': cur_website.thumbnail_panel_position,
            'interval_play': cur_website.interval_play,
            'enable_disable_text': cur_website.enable_disable_text,
            'color_opt_thumbnail': cur_website.color_opt_thumbnail,
            'change_thumbnail_size': cur_website.change_thumbnail_size,
            'thumb_height': cur_website.thumb_height,
            'thumb_width': cur_website.thumb_width,
        }
        return values

    @http.route(['/theme_furnito/category_image_effect_config'], type='json', auth='public', website=True)
    def category_image_dynamic_slider(self, **post):
        slider_data = request.env['furnito.category.slider.config'].search(
            [('id', '=', int(post.get('slider_id')))])
        values = {
            's_id': slider_data.name.lower().replace(' ', '-') + '-' + str(slider_data.id),
            'counts': slider_data.no_of_counts,
            'auto_rotate': slider_data.auto_rotate,
            'auto_play_time': slider_data.sliding_speed,
        }
        return values

    @http.route(['/theme_furnito/category_get_dynamic_slider'], type='http', auth='public', website=True)
    def category_get_dynamic_slider(self, **post):
        if post.get('slider-id'):
            slider_header = request.env['furnito.category.slider.config'].sudo().search(
                [('id', '=', int(post.get('slider-id')))])
            values = {
                'slider_header': slider_header
            }
            for category in slider_header.collections_category:
                cat_parent = request.env['product.public.category'].search([('parent_id', '=', category.id)])
                total_count = []
                if cat_parent:
                    for cat in cat_parent:
                        query = """
                            SELECT
                                count(website_published)
                            FROM
                                product_template
                            WHERE id in (
                                SELECT product_template_id
                                FROM product_public_category_product_template_rel
                                WHERE product_public_category_id in %s);
                            """
                        request.env.cr.execute(query, (tuple([cat.id]),))
                        prod_count = request.env.cr.fetchone()
                        total_count.append(prod_count)
                else:
                    query = """
                            SELECT
                                count(website_published)
                            FROM
                                product_template
                            WHERE id in (
                                SELECT product_template_id
                                FROM product_public_category_product_template_rel
                                WHERE product_public_category_id in %s);
                            """
                    request.env.cr.execute(query, (tuple([category.id]),))
                    prod_count = request.env.cr.fetchone()
                    total_count.append(prod_count)
                category.linked_product_count = sum([pair[0] for pair in total_count])

            values.update({
                'slider_details': slider_header.collections_category,
            })
            return request.render("theme_furnito.theme_furnito_cat_slider_view", values)

    # For multi product slider
    @http.route(['/theme_furnito/product_multi_get_options'], type='json', auth="public", website=True)
    def product_multi_get_slider_options(self):
        slider_options = []
        option = request.env['furnito.multi.slider.config'].search(
            [('active', '=', True)], order="name asc")
        for record in option:
            slider_options.append({'id': record.id,
                                   'name': record.name})
        return slider_options

    @http.route(['/theme_furnito/category_get_options'], type='json', auth="public", website=True)
    def category_get_slider_options(self):
        slider_options = []
        option = request.env['furnito.category.slider.config'].search(
            [('active', '=', True)], order="name asc")
        for record in option:
            slider_options.append({'id': record.id,
                                   'name': record.name})
        return slider_options

    @http.route(['/theme_furnito/product_multi_get_dynamic_slider'], type='http', auth='public', website=True)
    def product_multi_get_dynamic_slider(self, **post):
        context, pool = dict(request.context), request.env
        if post.get('slider-type'):
            slider_header = request.env['furnito.multi.slider.config'].sudo().search(
                [('id', '=', int(post.get('slider-type')))])

            if not context.get('pricelist'):
                pricelist = request.website.get_current_pricelist()
                context = dict(request.context, pricelist=int(pricelist))
            else:
                pricelist = pool.get('product.pricelist').browse(context['pricelist'])

            context.update({'pricelist': pricelist.id})
            from_currency = pool['res.users'].browse(SUPERUSER_ID).company_id.currency_id
            to_currency = pricelist.currency_id
            compute_currency = lambda price: pool['res.currency']._compute(from_currency, to_currency, price)
            for no in slider_header.no_of_collection:
                n_field = 'collection_' + no + '_ids'
                slider_obj = slider_header.sudo().read([n_field])
                for prod_id in slider_obj[0].get(n_field):
                    pro = pool['product.template'].browse([prod_id])
                    pro.custom_snip_price = pro.website_price

            values = {
                'slider_details': slider_header,
                'slider_header': slider_header,
                'compute_currency': compute_currency,
            }

            return request.render("theme_furnito.theme_furnito_multi_cat_slider_view", values)

    @http.route(['/theme_furnito/product_multi_image_effect_config'], type='json', auth='public', website=True)
    def product_multi_product_image_dynamic_slider(self, **post):
        slider_data = request.env['furnito.multi.slider.config'].search(
            [('id', '=', int(post.get('slider_type')))])
        values = {
            's_id': slider_data.no_of_collection + '-' + str(slider_data.id),
            'counts': slider_data.no_of_collection,
            'auto_rotate': slider_data.auto_rotate,
            'auto_play_time': slider_data.sliding_speed,
        }
        return values

        # For Featured Product slider
    @http.route(['/theme_furnito/featured_product_get_options'], type='json', auth="public", website=True)
    def featured_product_get_slider_options(self):
        slider_options = []
        option = request.env['furnito.feature.product.slider.config'].search(
            [('active', '=', True)], order="name asc")
        for record in option:
            slider_options.append({'id': record.id,
                                   'name': record.name})
        return slider_options

    @http.route(['/theme_furnito/featured_product_get_dynamic_slider'], type='http', auth='public', website=True)
    def featured_product_get_dynamic_slider(self, **post):
        context, pool = dict(request.context), request.env
        if post.get('slider-id'):
            slider_header = request.env['furnito.feature.product.slider.config'].sudo().search(
                [('id', '=', int(post.get('slider-id')))])

            if not context.get('pricelist'):
                pricelist = request.website.get_current_pricelist()
                context['pricelist'] = dict(request.context, pricelist=int(pricelist))
            else:
                pricelist = pool.get('product.pricelist').browse(context['pricelist'])

            context.update({'pricelist': pricelist.id})

            from_currency = pool['res.users'].browse(SUPERUSER_ID).company_id.currency_id
            to_currency = pricelist.currency_id
            compute_currency = lambda price: pool['res.currency']._compute(from_currency, to_currency, price)
            for prod in slider_header.feature_products_collections:
                prod.custom_snip_price = prod.website_price

            for prod in slider_header.on_sale_collections:
                prod.custom_snip_price = prod.website_price

            for prod in slider_header.random_products_collections:
                prod.custom_snip_price = prod.website_price

            for prod in slider_header.low_price_collections:
                prod.custom_snip_price = prod.website_price

            values = {
                'slider_header': slider_header,
                'compute_currency': compute_currency,
            }
            return request.render("theme_furnito.theme_furnito_featured_product_slider_view", values)

    @http.route(['/theme_furnito/featured_product_image_effect_config'], type='json', auth='public', website=True)
    def featured_product_image_dynamic_slider(self, **post):
        slider_data = request.env['furnito.feature.product.slider.config'].search(
            [('id', '=', int(post.get('slider_id')))])
        values = {
            's_id': slider_data.name.lower().replace(' ', '-') + '-' + str(slider_data.id),
            'counts': slider_data.no_of_counts,
            'auto_rotate': slider_data.auto_rotate,
            'auto_play_time': slider_data.sliding_speed,
        }
        return values


class ThemeFurnitoBrandSlider(WebsiteSale):

    @http.route(['/shop/pager_selection/<model("product.per.page.no"):pl_id>'], type='http', auth="public", website=True)
    def product_page_change(self, pl_id, **post):
        request.session['default_paging_no'] = pl_id.name
        main.PPG = pl_id.name
        return request.redirect('/shop' or request.httprequest.referrer)

    """
    @http.route(['/shop',
                 '/shop/page/<int:page>',
                 '/shop/category/<model("product.public.category"):category>',
                 '/shop/category/<model("product.public.category"):category>/page/<int:page>',
                 '/shop/brands'],
                type='http',
                auth='public',
                website=True)
    def shop(self, page=0, category=None, brand=None, search='', ppg=False, **post):
        context, pool = request.context, request.env
        if brand:
            request.context.setdefault('brand_id', int(brand))
        result = super(ThemeFurnitoBrandSlider, self).shop(
            page=page, category=category, brand=brand, search=search, **post)
        sort_order = ""
        cat_id = []
        page_no = request.env['product.per.page.no'].search([('set_default_check', '=', True)])
        if page_no:
            ppg = page_no.name
        else:
            ppg = main_shop.PPG
        product = []
        newproduct = []
        product_price=[]

        # product template object
        product_obj = pool.get('product.template')

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int, v.split("-")) for v in attrib_list if v]
        attributes_ids = set([v[0] for v in attrib_values])
        attrib_set = set([v[1] for v in attrib_values])
        domain = request.website.sale_product_domain()
        domain += self._get_search_domain(search, category, attrib_values)
        url = "/shop"

        if post:
            request.session.update(post)

        prevurl = request.httprequest.referrer
        if prevurl:
            if not re.search('/shop', prevurl, re.IGNORECASE):
                request.session['tag'] = ""
                request.session['sort_id'] = ""
                request.session['sortid'] = ""
                request.session['pricerange'] = ""
                request.session['min1'] = ""
                request.session['max1'] = ""

        session = request.session
        # for category filter
        if category:
            category = pool['product.public.category'].browse(int(category))
            url = "/shop/category/%s" % slug(category)

        if category != None:
            for ids in category:
                cat_id.append(ids.id)
            domain += ['|', ('public_categ_ids.id', 'in', cat_id),
                       ('public_categ_ids.parent_id', 'in', cat_id)]
        # for tag filter
        if session.get('tag'):
            session_tag = session.get('tag')
            tag = session_tag[0]
            tags_obj = pool['biztech.product.tags']
            tags_ids = tags_obj.search([])
            tags = tags_obj.browse( tags_ids)
            if tag:
                tag = pool['biztech.product.tags'].browse(int(tag))
                domain += [('biztech_tag_ids', '=', int(tag))]
                request.session["tag"] = [tag.id, tag.name]

        # For Product Sorting
        if session.get('sort_id'):
            session_sort = session.get('sort_id')
            sort = session_sort
            sorts_obj = pool['biztech.product.sortby']
            sorts_ids = sorts_obj.search( [])
            sorts = sorts_obj.browse( sorts_ids)
            sort_field = pool['biztech.product.sortby'].browse(int(sort))
            request.session['product_sort_name'] = sort_field.name
            order_field = sort_field.sort_on.name
            order_type = sort_field.sort_type
            sort_order = '%s %s' % (order_field, order_type)
            if post.get("sort_id"):
                request.session["sortid"] = [
                    sort, sort_order, sort_field.name, order_type]

        # For Price slider
        product_slider_ids = product_obj.search([])
        for product in product_slider_ids:
            product_price.append(product.website_price)

        if product_slider_ids:
            if post.get("range1") or post.get("range2") or not post.get("range1") or not post.get("range2"):
                range1 = min(product_price)
                range2 = max(product_price)
                result.qcontext['range1'] = range1
                result.qcontext['range2'] = range2

            if session.get("min1") and session["min1"]:
                post["min1"] = session["min1"]
            if session.get("max1") and session["max1"]:
                post["max1"] = session["max1"]
            if range1:
                post["range1"] = range1
            if range1:
                post["range2"] = range1

            if request.session.get('min1') or request.session.get('max1'):
                if request.session.get('min1'):
                    if request.session['min1'] != None:
                        for prod_id in product_withprice:
                            if product_withprice.get(prod_id) >= float(request.session['min1']) and product_withprice.get(prod_id) <= float(request.session['max1']):
                                product.append(prod_id)
                        request.session["pricerange"] = str(
                            request.session['min1'])+"-To-"+str(request.session['max1'])
                newproduct = product
                domain += [('id', 'in', newproduct)]

            if session.get('min1') and session['min1']:
                result.qcontext['min1'] = session["min1"]
                result.qcontext['max1'] = session["max1"]

        if request.session.get('default_paging_no'):
            ppg = int(request.session.get('default_paging_no'))

        product_count = product_obj.search_count(domain)
        pager = request.website.pager(
            url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
        product_ids = product_obj.search(
            domain, limit=ppg, offset=pager['offset'], order=sort_order)

        result.qcontext.update({'product_count': product_count})
        result.qcontext.update({'products': product_ids})
        result.qcontext.update({'category': category})
        result.qcontext.update({'pager': pager})

        result.qcontext.update(
            {'bins': TableCompute().process(product_ids, ppg)})

        result.qcontext['brand'] = brand
        result.qcontext['brand_obj'] = request.env['product.brands'].sudo().search([('id', '=', brand)])

        return result
    """

    @http.route()
    def cart_update_json(self, product_id, line_id=None, add_qty=None, set_qty=None, display=True):
        result = super(ThemeFurnitoBrandSlider, self).cart_update_json(product_id, line_id, add_qty, set_qty, display)
        order = request.website.sale_get_order()
        result.update({'theme_furnito.hover_total': request.env['ir.ui.view'].render_template("theme_furnito.hover_total", {
                'website_sale_order': order })
            })
        return result

    @http.route(['/furnito_theme/get_brand_slider'], type='http', auth='public', website=True)
    def get_brand_slider(self, **post):
        keep = QueryURL('/furnito_theme/get_brand_slider', brand_id=[])

        value = {
            'website_brands': False,
            'brand_header': False,
            'keep': keep
        }

        if post.get('brand_count'):
            brand_data = request.env['product.brands'].search(
                [], limit=int(post.get('brand_count')))
            if brand_data:
                value['website_brands'] = brand_data

        if post.get('brand_label'):
            value['brand_header'] = post.get('brand_label')

        return request.render("theme_furnito.theme_furnito_brand_slider_view", value)

    @http.route(['/theme_furnito/removeattribute'], type='json', auth='public', website=True)
    def remove_selected_attribute(self, **post):
        if post.get("attr_remove"):
            remove = post.get("attr_remove")
            if remove == "pricerange":
                del request.session['min1']
                del request.session['max1']
                request.session[remove] = ''
                return True
            elif remove == "sortid":
                request.session[remove] = ''
                request.session["sort_id"] = ''
                return True
            elif remove == "tag":
                request.session[remove] = ''
                return True
