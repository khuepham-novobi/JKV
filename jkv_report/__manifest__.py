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
    'name': 'JKV: Report',
    'version': '1.0',
    'summary': 'Report Download and Subscription',
    'author': 'Novobi LLC',
    'depends': [
        'jkv_product','jkv_website_purchase'
    ],
    'data': [
        'data/data.xml',
        'views/jkv_subscription_views.xml',
        'views/jkv_download_views.xml',
        'views/res_partner_views.xml',
        'wizard/jkv_subscription_report.xml',
        'wizard/jkv_download_report.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: