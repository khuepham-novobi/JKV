
from odoo import api, fields, models


class ProductPublicCategory(models.Model):

    _inherit = 'product.public.category'

    linked_product_count = fields.Integer(string='# of Products')
    include_in_megamenu = fields.Boolean(
        string="Include in mega menu", help="Include in mega menu")
    menu_id = fields.Many2one('website.menu', string="Main menu")
    description = fields.Text(string="Description",
                              help="Short description which will be visible below category slider.")
