# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Copyright (C) 2015 Novobi LLC (<http://novobi.com>)
#
##############################################################################


{
    'name': 'JKV: Signup',
    'version': '1.0',
    'summary': 'Register',
    'author': 'Novobi LLC',
    'depends': [
        'auth_signup','website_portal','sale','jkv_product','jkv_show_event'
        ],
    'data': [
        'views/template.xml',
        'views/res_partner_view.xml',
        'views/assets.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
