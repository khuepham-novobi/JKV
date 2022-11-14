from odoo import api, fields, models, tools

class JKVBlog(models.Model):
    _name = "jkv.blog"
    _rec_name = "blog_title"

    blog_title = fields.Char(string='Title', required=True)
    blog_date = fields.Date(string='Date', required=True)
    blog_author = fields.Many2one('res.partner', 'Author', default=lambda self: self.env.user.partner_id)
    blog_content = fields.Html(string ="Article Body", required=True)
    blog_image = fields.Binary(string='Image', help="Select image here", attachment=True)
    blog_tags = fields.Many2many(comodel_name='jkv.tag', string='Tags')

    blog_image_medium = fields.Binary(
        "Medium-sized image", compute='_compute_images')

    @api.one
    @api.depends('blog_image')
    def _compute_images(self):
        resized_images = tools.image_get_resized_images(self.blog_image, return_big=True,
                                                        avoid_resize_medium=True)
        self.blog_image_medium = resized_images['image_medium']


    def _format_date(self, date):
        month_switcher = {
            '01': 'JANUARY',
            '02': 'FEBRUARY',
            '03': 'MARCH',
            '04': 'APRIL',
            '05': 'MAY',
            '06': 'JUNE',
            '07': 'JULY',
            '08': 'AUGUST',
            '09': 'SEPTEMBER',
            '10': 'OCTOBER',
            '11': 'NOVEMBER',
            '12': 'DECEMBER',
        }
        month = month_switcher.get(date[5:7], "Invalid month of years")
        return month + " " + date[0:4]

    def _format_blog_date(self, date):
        month_switcher = {
            '01': 'JANUARY',
            '02': 'FEBRUARY',
            '03': 'MARCH',
            '04': 'APRIL',
            '05': 'MAY',
            '06': 'JUNE',
            '07': 'JULY',
            '08': 'AUGUST',
            '09': 'SEPTEMBER',
            '10': 'OCTOBER',
            '11': 'NOVEMBER',
            '12': 'DECEMBER',
        }
        month = month_switcher.get(date[5:7], "Invalid month of years")
        return month + " " + date[8:10] + ", " + date[0:4]

    def compute_blog_archive(self):
        for i in range(len(self)):
            self[i].blog_archive = self[i]._format_date(self[i].blog_date)

    def compute_blog_date(self):
        for i in range(len(self)):
            self[i].blog_date_view = self[i]._format_blog_date(self[i].blog_date)

    blog_archive = fields.Char(compute=compute_blog_archive, store=False)
    blog_date_view = fields.Char(compute=compute_blog_date, store=False)
