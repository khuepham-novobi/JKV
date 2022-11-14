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
    'name': 'JKV: Website Purchase',
    'version': '1.0',
    'summary': 'Website Sale',
    'author': 'Novobi LLC',
    'depends': [
        'website','jkv_product','jkv_show_event','website_portal','theme_furnito','sale','website_payment','account_taxcloud'
    ],
    'data': [
        'views/templates.xml',
        'views/jkv_show_venue_view.xml',
        'data/mail_data.xml',
        'data/data.xml',
        'security/ir.model.access.csv', 
        'wizard/jkv_set_price_view.xml'
    ],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
