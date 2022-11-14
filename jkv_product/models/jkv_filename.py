import logging
import pytz
from datetime import datetime, date, time, timedelta

from boto.s3.connection import S3Connection

from odoo import api, fields, models,SUPERUSER_ID, _
from odoo.exceptions import Warning, ValidationError

from .s3_helper import S3Helper


_logger = logging.getLogger(__name__)


class JKVRiderExtend(models.Model):
    _inherit = 'jkv.rider'
    
    video_ids = fields.One2many('jkv.filename','rider_id',string='Videos')
    list_ride_number = fields.Char(string='List of ride number',compute='_get_ride_number',store=True)
    
    @api.depends('video_ids','video_ids.ride_number')
    def _get_ride_number(self):
        for record in self:
            d = set()
            for video in record.video_ids:
                if video.ride_number:
                    d.add(video.ride_number)
            strs = ''
            if d:
                for e in d:
                    strs = strs + '-' + str(e)
                record.list_ride_number = strs
            else:
                record.list_ride_number = False


class JKVFileName(models.Model):
    _name = 'jkv.filename'

    name = fields.Char(string='File Name', compute='_compute_file_name', store=True, index=True)
    rider_id = fields.Many2one('jkv.rider', string='Rider', ondelete='restrict')
    rider_number = fields.Integer(string='Rider Number', related='rider_id.rider_number')
    show_id = fields.Many2one('jkv.show.venue', string='Show name', ondelete='restrict', index=True)
    show_number = fields.Integer(string='Show Number', related='show_id.show_number')
    class_id = fields.Many2one('jkv.class',string='Class Name',ondelete='restrict')
    class_number = fields.Integer(string='Class Number', related='class_id.class_number') 
    video_filename_url = fields.Char(string='Video Filename', store=True, compute='_compute_video_filename_url')
    signed_filename_url = fields.Char(string='Signed Video Filename', compute='_compute_signed_filename_url')
    sample_file_url = fields.Char(string='Sample File', store=True, compute='_compute_sample_file_url')
    watermark_file_url = fields.Char(string='Watermark File', compute='_compute_watermark_file_url')
    ride_number = fields.Integer(string='Ride Number')
      
    @api.model
    def get_file_on_s3(self):
        # Skip running schedule at these specific time
        now = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone('US/Central'))
        hour_float = now.hour + now.minute / 60 + now.second / 3600
        hour_float = (hour_float + 24) if hour_float < 12 else hour_float
        if 22.5 <= hour_float < 24 or 24.5 <= hour_float < 30:
            return

        aws_access_key_id = self.env.ref('jkv_product.aws_access_key_id').value
        aws_secret_access_key = self.env.ref('jkv_product.aws_secret_access_key').value
        conn = S3Connection(aws_access_key_id,aws_secret_access_key)
        bucket_name = self.env['ir.config_parameter'].get_param('bucket_name')
        bucket = conn.get_bucket(bucket_name)
        # ShowNumber-ClassNumber-RiderNumber-Ride #
        all_filename = set(key.name.replace('-000', '-')
                           for key in bucket.list()
                           if all(key.name.find(suffix) < 0 for suffix in ('sample', 'watermark')) and not key.name.startswith('L-'))
        records = self.sudo().search_read([], ['name'])
        list_file_name = all_filename - set(r['name'] for r in records)

        video_extension_mp4 = self.env['ir.config_parameter'].sudo().get_param('jkv_product.filename_extension_mp4')
        miss_file = []
        for file_name in list_file_name:
            try:
                e = file_name.split('-')
                if len(e) != 4:
                    miss_file.append(file_name)
                    continue

                show_number = e[0]
                class_number = e[1]
                rider_number = e[2]
                ride_number = e[3].replace(video_extension_mp4,'')                

                show = self.env['jkv.show.venue'].sudo().search([('show_number','=',show_number)],limit=1)

                class_show = self.env['jkv.class'].sudo().search([('class_number','=',class_number)],limit=1)

                rider = self.env['jkv.rider'].sudo().search([('rider_number','=',rider_number),('show_number','=',show_number)],limit=1)

                if not show or not class_show or not rider:
                    miss_file.append(file_name)
                    continue
                    
                try:
                    self.sudo().create({'name':file_name,'rider_id':rider.id,'class_id':class_show.id,'show_id':show.id,'ride_number':ride_number})
                except Exception as e:
                    logging.error("Error while creating filename: %s, %s", e, file_name)
                    miss_file.append(file_name)
                    
            except Exception as e:
                logging.error("Error while processing S3 files: %s", e)
                miss_file.append(file_name)

        if miss_file:

            if len(miss_file) == 1 and miss_file[0] == 'public':
                return

            template = self.env['ir.model.data'].sudo().get_object('jkv_product', 'error_create_file')
            mail_template_obj = self.env['mail.template']
            mail_template_obj._ids = [template.id]
            admin_id = False
            try:
                admin_id = self.env.ref('base.jkv_admin').id
                mail_template_obj.with_context(subject='[JKV]Error: Create video file',content=miss_file).sudo().send_mail(admin_id,force_send=True, raise_exception=False,email_values=None)
            except:
                mail_template_obj.with_context(subject='[JKV]Error: Create video file',content=miss_file).sudo().send_mail(SUPERUSER_ID,force_send=True, raise_exception=False,email_values=None)

    @api.model
    def check_video_filename_url(self):
        records = self.search([])
        video_files = []
        
        aws_access_key_id = self.env.ref('jkv_product.aws_access_key_id').value
        aws_secret_access_key = self.env.ref('jkv_product.aws_secret_access_key').value

        conn = S3Connection(aws_access_key_id,aws_secret_access_key)
        bucket_name = self.env['ir.config_parameter'].get_param('bucket_name')
        bucket = conn.get_bucket(bucket_name)
        set_file_name = set(key.name.encode('utf-8') for key in bucket.list())

        for record in records:
            if record.name not in set_file_name:
                video_files.append(record.name)
            
        if video_files:
            template = self.env['ir.model.data'].sudo().get_object('jkv_product', 'error_file_access')
            mail_template_obj = self.env['mail.template']
            mail_template_obj._ids = [template.id]
            admin_id = False
            try:
                admin_id = self.env.ref('base.jkv_admin').id
                mail_template_obj.with_context(subject='[JKV]Error: Access file',content=video_files).sudo().send_mail(admin_id,force_send=True, raise_exception=False,email_values=None)
            except:
                mail_template_obj.with_context(subject='[JKV]Error: Access file',content=video_files).sudo().send_mail(SUPERUSER_ID,force_send=True, raise_exception=False,email_values=None)

    @api.constrains('show_id', 'class_id', 'rider_id', 'ride_number')
    def _check_filename_unique(self):
        records = self.search([('show_number','=', self.show_number),('class_number', '=', self.class_number),('rider_number', '=', self.rider_number),('ride_number', '=', self.ride_number)], limit=2)
        if len(records) >=2:
            raise ValidationError('Show Number, Class Number, Rider Number, Ride Number is a unique combination!')

    #ShowNumber-ClassNumber-RiderNumber-Ride#
    @api.depends('rider_id.rider_number','show_id.show_number','class_id.class_number','ride_number','class_id','show_id','rider_id')
    def _compute_file_name(self):
        video_extension_mp4 = self.env['ir.config_parameter'].sudo().get_param('jkv_product.filename_extension_mp4')
        for video in self:            
            video.name = str(video.show_number) + '-' + str(video.class_number) + '-' + str(video.rider_number) + '-' + str(video.ride_number) + video_extension_mp4

    @api.depends('rider_id.rider_number','show_id.show_number','class_id.class_number','ride_number','class_id','show_id','rider_id')
    def _compute_video_filename_url(self):
        IrConfigParam = self.env['ir.config_parameter']
        video_path = IrConfigParam.sudo().get_param('jkv_product.filename_path')
        video_extension_mp4 = IrConfigParam.sudo().get_param('jkv_product.filename_extension_mp4')
        for video in self:
            video.video_filename_url = video_path + str(video.show_number) + '-' + str(video.class_number) + '-' + str(video.rider_number) + '-' + str(video.ride_number) + video_extension_mp4

    @api.depends('rider_id.rider_number','show_id.show_number','class_id.class_number','ride_number','class_id','show_id','rider_id')
    def _compute_sample_file_url(self):
        IrConfigParam = self.env['ir.config_parameter']
        video_path = IrConfigParam.sudo().get_param('jkv_product.filename_path')
        video_extension_mp4 = IrConfigParam.sudo().get_param('jkv_product.filename_extension_mp4')
        for video in self:
            video.sample_file_url = '%spublic/%s-%s-%s-%s-sample%s' % (video_path, str(video.show_number), str(video.class_number),
                                                                       str(video.rider_number), str(video.ride_number), video_extension_mp4)

    def _compute_watermark_file_url(self):
        """
        Sign again every time this field is requested
        """
        IrConfigParam = self.env['ir.config_parameter'].sudo()
        video_extension_mp4 = IrConfigParam.get_param('jkv_product.filename_extension_mp4')
        video_path = IrConfigParam.get_param('jkv_product.filename_path')
        s3_helper = S3Helper(self.env)
        expiration_duration = 6 * 60 * 60
        for video in self:
            video_name = video.video_filename_url.replace(video_path, '')
            watermark_video_name = 'watermark/' + video_name.replace(video_extension_mp4, '-watermark%s' % video_extension_mp4)
            url = s3_helper.generate_presigned_get_object(watermark_video_name, expiration_duration)
            video.watermark_file_url = url or ''

    def _compute_signed_filename_url(self):
        """
        Sign again every time this field is requested
        """
        IrConfigParam = self.env['ir.config_parameter'].sudo()
        video_path = IrConfigParam.get_param('jkv_product.filename_path')
        s3_helper = S3Helper(self.env)
        expiration_duration = 6 * 60 * 60
        for video in self:
            video_filename = video.video_filename_url.replace(video_path, '')
            url = s3_helper.generate_presigned_get_object(video_filename, expiration_duration)
            video.signed_filename_url = url or ''

    @api.multi
    def unlink(self):
        if not self.env.context.get('product_remove',False):
            product_ids = self.env['product.template'].sudo().search([('filename_id.id','in',self._ids)])._ids
            Product = self.env['product.template']
            Product._ids = product_ids
            Product.sudo().with_context(video_remove=True).unlink()
        return super(JKVFileName, self).unlink()
        
    @api.model
    def create(self, vals):
        result = super(JKVFileName, self).create(vals)
        """
            Create product automatically
        """
        values = {
            'name': result.name,
            'filename_id': result.id,
            'website_published':True,
            'list_price':self.env.ref('jkv_website_purchase.product_price').value
        }
        self.env['product.template'].create(values)

        return result