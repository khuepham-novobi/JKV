{
    'name': 'JKV: Show Event',
    'version': '1.0',
    'summary': 'Show Event',
    'author': 'Novobi LLC',
    'depends': ['product'],
    'data': [
    	'view/jkv_show_venue_view.xml',
        'view/jkv_class_view.xml',
        'view/jkv_rider_view.xml',
    	'view/res_partner_view.xml',
        'security/ir.model.access.csv',
        'wizard/jkv_find_class.xml',
        'wizard/jkv_find_show.xml',
        'wizard/jkv_find_rider.xml',
        'wizard/jkv_export_customer.xml',
        'data/ir_sequence.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}