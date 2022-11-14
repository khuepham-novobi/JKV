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
    'name': 'JKV: Customer Support',
    'version': '1.0',
    'summary': 'JKV Customer Support',
    'author': 'Novobi LLC',
    'depends': [
        'jkv_website_sale'
        ],
    'data': [
        'views/customer_support_views.xml',
        'data/lead_email_template.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: