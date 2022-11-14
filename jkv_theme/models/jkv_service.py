from odoo import api, fields, models, tools


class JKVService(models.Model):
    _name = "jkv.service"
    _rec_name = "service_name"

    service_name = fields.Text("Name")
    is_general_service = fields.Boolean("General", default=False)
    title = fields.Char(string="Title")
    content = fields.Html(string='Content')
    image = fields.Binary(string='Image', help="Select image here", attachment=True)
    image_medium = fields.Binary(
        "Medium-sized image", compute='_compute_images')

    @api.one
    @api.depends('image')
    def _compute_images(self):
        resized_images = tools.image_get_resized_images(self.image, return_big=True,
                                                        avoid_resize_medium=True)
        self.image_medium = resized_images['image_medium']
