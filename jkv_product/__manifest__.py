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
    'name': 'JKV: Product',
    'version': '1.0',
    'summary': 'Video Product',
    'author': 'Novobi LLC',
    'depends': [
        'jkv_show_event','product'
        ],
    'data': [
    	'views/product_template_views.xml',
        'views/jkv_filename_views.xml',
        'data/jkv_filename_path.xml',
        'data/data.xml',
        'data/mail_data.xml',
        'data/base_action_rule_data.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: