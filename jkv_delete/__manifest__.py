# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Copyright (C) 2018 Novobi LLC (<http://novobi.com>)
#
##############################################################################


{
    'name': 'JKV: Delete',
    'version': '1.1',
    'summary': 'Show Delete Flow',
    'author': 'Novobi LLC',
    'depends': [
        'jkv_product',
        'jkv_report',
        'jkv_website_purchase'
    ],
    'data': [
        'data/product_product_data.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: