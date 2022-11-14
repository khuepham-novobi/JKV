# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Copyright (C) 2019 Novobi LLC (<http://novobi.com>)
#
##############################################################################


{
    'name': 'JKV Theme',
    'version': '1.0',
    'author': 'Novobi LLC',
    'depends': [
        'website_sale',
        'jkv_events_calendar',
        'jkv_signup',
    ],
    'data': [
        'data/website_crm_data.xml',
        'data/website_partner_data.xml',
        'data/jkv_service_data.xml',
        'data/jkv_livestream_data.xml',
        'data/base_action_rule_data.xml',
        'data/jkv_call_to_action_data.xml',
        'data/jkv_website_menu_data.xml',
        'data/auth_signup_data.xml',

        'views/common.xml',
        'views/assets.xml',
        'views/footer.xml',
        'views/header.xml',
        'views/homepage.xml',
        'views/contact_us.xml',
        'views/signup_login.xml',
        'views/account_videos.xml',
        'views/calendar.xml',
        'views/account_edit.xml',
        'views/products.xml',
        'views/video_archive.xml',
        'views/checkout.xml',
        'views/videos.xml',
        'views/subscription.xml',
        'views/terms.xml',
        'views/privacy.xml',
        'views/thanks.xml',
        'views/live_stream.xml',
        'views/blog.xml',
        'views/blog_article.xml',
        'views/blog_article_details.xml',
        'views/jkv_service_views.xml',
        'security/ir.model.access.csv',
        'views/call_to_action.xml',
        'views/event_calendar.xml',
        'views/event_livestream_calendar.xml',
        'views/pricing.xml',
        'views/jk_download.xml',
        'views/jk_ringside.xml',
        'views/jk_stream.xml',
        'views/services.xml',
        'views/website_template.xml',
        'views/res_config_views.xml',
    ],
    'qweb': [
        "static/src/xml/subscription.xml",
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
