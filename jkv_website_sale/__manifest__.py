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
    'name': 'JKV: Website sale',
    'version': '1.0',
    'summary': 'Website Sale',
    'author': 'Novobi LLC',
    'depends': [
        'jkv_product',
        'jkv_signup',
        'website',
        'website_sale',
        'theme_furnito'
    ],
    'data': [
        'data/base_action_rule_data.xml',
        'views/website_sale_template.xml',
        'views/assets.xml',
        'views/hide_menu.xml',
        'security/base_security.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
