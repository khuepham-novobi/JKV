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
    'name': 'JKV: Events Calendar',
    'version': '1.0',
    'summary': 'Events Calendar',
    'author': 'Novobi LLC',
    'depends': [
        'jkv_website_sale'
    ],
    'data': [
        'views/template.xml',
        'views/events_calendar_view.xml',
        'views/assets.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
