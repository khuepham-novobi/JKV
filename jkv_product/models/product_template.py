from odoo import api, fields, models,  _
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import logging
from datetime import datetime
import pytz
from boto.s3.connection import S3Connection
from odoo import api, fields, models,SUPERUSER_ID
from .s3_helper import S3Helper

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    jkv_video_rider_ids = fields.One2many('product.template', 'rider_id', string='JKV Videos')
    jkv_video_trainer_ids = fields.One2many('product.template', 'trainer_id', string='JKV Videos')
    jkv_video_owner_ids = fields.One2many('product.template', 'owner_id', string='JKV Videos')
        

class ProductTemplate(models.Model):

    _inherit = 'product.template'

    filename_id = fields.Many2one('jkv.filename', string='Video Filename')
    rider_name = fields.Char(string='Rider Name', related='filename_id.rider_id.rider_name')
    rider_number = fields.Integer(string='Rider Number', related='filename_id.rider_number')
    show_name = fields.Char(string='Show Name', related='filename_id.show_id.name')
    show_number = fields.Integer(string='Show Number', related='filename_id.show_number')
    class_name = fields.Char(string='Class Name', related='filename_id.class_id.name')
    class_number = fields.Integer(string='Class Number', related='filename_id.class_number')
    post_date = fields.Date(string='Post Date', related='filename_id.show_id.end_date')
    ride_number = fields.Integer(string='Ride Number', related='filename_id.ride_number')
    video_filename_url = fields.Char(string='Video URL', related='filename_id.video_filename_url')
    signed_filename_url = fields.Char(string='Signed Video URL', related='filename_id.signed_filename_url')
    sample_file_url = fields.Char(string='Sample File', related='filename_id.sample_file_url')
    watermark_file_url = fields.Char(string='Watermark File', related='filename_id.watermark_file_url')
    horse_name = fields.Char(string='Horse Name', related='filename_id.rider_id.horse_name')
    post_day = fields.Char(string='Post Day', compute='_compute_post_day',store=True)
    rider_id = fields.Many2one('res.partner',related='filename_id.rider_id.rider_id')
    trainer_id = fields.Many2one('res.partner',related='filename_id.rider_id.trainer_id')
    owner_id = fields.Many2one('res.partner',related='filename_id.rider_id.owner_id')
    
    _sql_constraints = [
        ('jkv_product_template_product_url_uniq', 'unique(filename_id)', 'File Name must be unique!'),
    ]

    is_livestream_product = fields.Boolean(string='Is Livestream Record?')
    livestream_show_id = fields.Many2one('jkv_livestream.show', string='Show Name')
    livestream_show_number = fields.Integer(string='Show Number')
    livestream_class_id = fields.Many2one('jkv_livestream.class', string='Class Name')
    livestream_class_number = fields.Integer(string='Class Number')
    livestream_date = fields.Datetime(string='Livestream Date')
    livestream_video_filename_url = fields.Char(string='Video URL')
    livestream_video_sample_file_url = fields.Char(string='Sample Video URL')
    livestream_signed_filename_url = fields.Char(string='Signed Video Filename', compute='_compute_livestream_signed_filename_url')
    
    @api.multi
    def unlink(self):
        if not self.env.context.get('video_remove',False):
            video_ids = self.env['jkv.filename'].sudo().search([('id','in',[record.filename_id.id for record in self])])._ids
            VideoModel = self.env['jkv.filename']
            VideoModel._ids = video_ids
            VideoModel.sudo().with_context(product_remove=True).unlink()
        return super(ProductTemplate, self).unlink()

    @api.depends('post_date')
    def _compute_post_day(self):

        DAY = {
            0:"Monday",
            1:"Tuesday",
            2:"Wednesday ",
            3:"Thursday",
            4:"Friday",
            5:"Saturday",
            6:"Sunday",
        }

        for product in self:
            if product.filename_id:
                product.post_day = ""
                post_day_index = datetime.strptime(product.post_date, '%Y-%m-%d').date().weekday()
                for index,day in DAY.items():
                    if post_day_index == index:
                        product.post_day = day

    @api.model
    def get_livestream_file_on_s3(self):
        # Skip running schedule at these specific time
        now = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone('US/Central'))
        hour_float = now.hour + now.minute / 60 + now.second / 3600
        hour_float = (hour_float + 24) if hour_float < 12 else hour_float
        if 22.5 <= hour_float < 24 or 24.5 <= hour_float < 30:
            return

        aws_access_key_id = self.env.ref('jkv_product.aws_access_key_id').value
        aws_secret_access_key = self.env.ref('jkv_product.aws_secret_access_key').value
        conn = S3Connection(aws_access_key_id, aws_secret_access_key)
        bucket_name = self.env['ir.config_parameter'].get_param('bucket_name')
        bucket = conn.get_bucket(bucket_name)
        # L-ShowNumber-ClassNumber-Day-Time #
        all_filename = set(key.name.replace('-000', '-')
                           for key in bucket.list()
                           if all(key.name.find(suffix) < 0 for suffix in ('sample', 'watermark')) and key.name.startswith('L-'))
        live_records = self.sudo().search_read([('is_livestream_product', '=', True)], ['name'])
        list_file_name = all_filename - set(r['name'] for r in live_records)

        video_extension_mp4 = self.env['ir.config_parameter'].sudo().get_param('jkv_product.filename_extension_mp4')
        IrConfigParam = self.env['ir.config_parameter']
        video_path = IrConfigParam.sudo().get_param('jkv_product.filename_path')
        miss_file = []
        for file_name in list_file_name:
            try:
                e = file_name.split('-')
                if len(e) != 5:
                    miss_file.append(file_name)
                    continue

                show_number = e[1]
                class_number = e[2]
                date_str = e[3]
                time_str = e[4].replace(video_extension_mp4, '')

                live_show = self.env['jkv_livestream.show'].sudo().search([('show_number', '=', show_number)], limit=1)

                live_class = self.env['jkv_livestream.class'].sudo().search([('class_number', '=', class_number)], limit=1)

                live_date = datetime.strptime('%s%s' % (date_str, time_str), "%Y%m%d%H%M")

                if not live_show or not live_class or not live_date:
                    miss_file.append(file_name)
                    continue

                try:
                    values = {
                        'name': file_name,
                        'website_published': True,
                        'livestream_show_id': live_show.id,
                        'livestream_class_id': live_class.id,
                        'livestream_show_number': show_number,
                        'livestream_class_number': class_number,
                        'livestream_date': live_date,
                        'livestream_video_filename_url': '%s%s' %(video_path, file_name),
                        'livestream_video_sample_file_url': '%spublic/%s-sample%s' %(video_path, file_name.replace(video_extension_mp4, ''), video_extension_mp4),
                        'is_livestream_product': True,
                        'list_price': self.env.ref('jkv_website_purchase.product_price').value
                    }
                    self.sudo().create(values)
                except Exception as e:
                    logging.error("Error while creating livestream filename: %s, %s", e, file_name)
                    miss_file.append(file_name)

            except Exception as e:
                logging.error("Error while processing S3 files: %s", e)
                miss_file.append(file_name)

        if miss_file:
            template = self.env['ir.model.data'].sudo().get_object('jkv_product', 'error_create_livestream_file')
            mail_template_obj = self.env['mail.template']
            mail_template_obj._ids = [template.id]
            try:
                admin_id = self.env.ref('base.jkv_admin').id
                mail_template_obj.with_context(subject='[JKV]Error: Create video file',
                                               content=miss_file).sudo().send_mail(admin_id, force_send=True,
                                                                                   raise_exception=False,
                                                                                   email_values=None)
            except:
                mail_template_obj.with_context(subject='[JKV]Error: Create video file',
                                               content=miss_file).sudo().send_mail(SUPERUSER_ID, force_send=True,
                                                                                   raise_exception=False,
                                                                                   email_values=None)

    def _compute_livestream_signed_filename_url(self):
        """
        Sign again every time this field is requested
        """
        IrConfigParam = self.env['ir.config_parameter'].sudo()
        video_path = IrConfigParam.get_param('jkv_product.filename_path')
        s3_helper = S3Helper(self.env)
        expiration_duration = 6 * 60 * 60
        for video in self:
            video_filename = video.livestream_video_filename_url.replace(video_path, '')
            url = s3_helper.generate_presigned_get_object(video_filename, expiration_duration)
            video.livestream_signed_filename_url = url or ''


class LivestreamShowEvent(models.Model):
    _name = 'jkv_livestream.show'

    name = fields.Char(string='Show Name', required=True)
    show_number = fields.Integer(string='Show Number', required=True)
    show_location = fields.Char(string='Show Location')
    start_date = fields.Date(string='Start Date', default=fields.Date.context_today, required=True)
    end_date = fields.Date(string='End Date', default=fields.Date.context_today, required=True)
    page_url_id = fields.Many2one('jkv.livestream', string='Page URL')

    _sql_constraints = [
        ('jkv_livestream_show_number_uniq', 'unique(show_number)', 'Show Number must be unique!'),
    ]

    @api.constrains('start_date', 'end_date')
    def _check_date(self):
        if self.start_date > self.end_date:
            raise ValidationError("Start Date must be less or equal than End Date")
        now = datetime.now()
        now = now.strftime(DEFAULT_SERVER_DATE_FORMAT)
        # if self.end_date < now:
        #     raise ValidationError("End Date entered must be after current day")


class LivestreamClass(models.Model):
    _name = 'jkv_livestream.class'

    name = fields.Char(string='Class Name', required=True)
    class_number = fields.Integer(string='Class Number', required=True)

    _sql_constraints = [
        ('jkv_livestream_class_number_uniq', 'unique(class_number)', 'Class Number must be unique!'),
    ]
