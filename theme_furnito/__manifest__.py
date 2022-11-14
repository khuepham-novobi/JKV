# -*- coding: utf-8 -*-
# Part of AppJetty. See LICENSE file for full copyright and licensing details.

{
    'name': 'Theme Furnito',
    'summary': 'HTML5 Bootstrap Ecommerce Theme for Furniture Industry',
    'description': '''Theme Furnito
Furniture industry
Wooden industry
''',
    'category': 'Theme/Ecommerce',
    'version': '10.0.1.0.3',
    'author': 'AppJetty',
    'website': 'https://goo.gl/XeYOAQ',
    'depends': [
        'website_sale',
        'mass_mailing',
        'website_blog',
    ],
    'data': [
        'views/assets.xml',
        'security/ir.model.access.csv',
        'views/slider_view.xml',
        'views/product_view.xml',
        'views/snippets.xml',
        'views/website_config_view.xml',
        'views/theme_customize.xml',
        'data/data.xml',
        'views/theme.xml',
        'views/homepage.xml',
        'views/reset_password.xml'
    ],
    'demo': [
        # 'data/demo_homepage.xml',
    ],
    'application': True,
    'live_test_url': 'http://theme-furnito.appjetty.com/',
    'images': ['static/description/splash-screen.png'],
    'price': 109.00,
    'currency': 'EUR',
}
