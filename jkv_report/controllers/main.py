# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import serialize_exception,content_disposition
import base64
import ast
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime
try:
    import xlwt
except ImportError:
    xlwt = None
   
class Export(http.Controller):

    def _format_date(self,date):
        date = datetime.strptime(date, DEFAULT_SERVER_DATE_FORMAT)
        return datetime.strftime(date,"%m/%d/%Y")
        
    @http.route('/subscription_record/export', type='http', auth='user')
    def export_subcription_records (self,record_ids,**kwargs):
    
        workbook = xlwt.Workbook()
        ids = ast.literal_eval(record_ids)
        records = request.env['jkv.subscription'].sudo().browse(ids)
        
        worksheet = workbook.add_sheet("Sheet1",cell_overwrite_ok=True)
        
        xlwt.add_palette_colour("background_header", 0x23)
        workbook.set_colour_RGB(0x23, 195, 134, 71)
        
        bold = xlwt.easyxf("font: bold on;")
        align_right = xlwt.easyxf("align: horiz right")
        align_left = xlwt.easyxf("align: horiz left")
        
        align_center = xlwt.easyxf("align: horiz center,wrap on")
        header = xlwt.easyxf("font: bold on,colour white;align: horiz center,wrap on;borders:bottom thin,bottom_color white;pattern: pattern solid, fore_colour background_header")

        bold_center = xlwt.easyxf("font: bold on;align: horiz center,wrap on")
        
        worksheet.write(0,0,'User',header)
        worksheet.write(0,1,'Show',header)
        worksheet.write(0,2,'Expiry Date',header)
        worksheet.write(0,3,'Type',header)
        
        worksheet.col(0).width = 256 * 15
        worksheet.col(1).width = 256 * 22
        worksheet.col(2).width = 256 * 18
        worksheet.col(3).width = 256 * 10
        
        row = 1
        for record in records:
            user_name = record.user_id.partner_id.name
            show = 'All shows' if record.all_shows else record.show_id.name
            type = record.type.title()
            expiry_date = self._format_date(record.expiry_date)
            worksheet.write(row,0,user_name,align_left)
            worksheet.write(row,1,show,align_left)
            worksheet.write(row,2,expiry_date,align_right)
            worksheet.write(row,2,type,align_left)
            row = row + 1
            
        now = datetime.strftime(datetime.now(),"%m-%d-%y")
        filename = 'Subcription_Data_Export_'+now+'.xls'
        response = request.make_response(None,
            headers=[('Content-Type', 'application/vnd.ms-excel'),
                    ('Content-Disposition', 'attachment; filename='+filename)])
        workbook.save(response.stream)

        return response 
        
    @http.route('/download_record/export', type='http', auth='user')
    def export_download_records (self,record_ids,**kwargs):
    
        workbook = xlwt.Workbook()
        ids = ast.literal_eval(record_ids)
        records = request.env['jkv.download'].sudo().browse(ids)
        
        worksheet = workbook.add_sheet("Sheet1",cell_overwrite_ok=True)
        
        xlwt.add_palette_colour("background_header", 0x23)
        workbook.set_colour_RGB(0x23, 195, 134, 71)
        
        bold = xlwt.easyxf("font: bold on;")
        align_right = xlwt.easyxf("align: horiz right")
        align_left = xlwt.easyxf("align: horiz left")
        
        align_center = xlwt.easyxf("align: horiz center,wrap on")
        header = xlwt.easyxf("font: bold on,colour white;align: horiz center,wrap on;borders:bottom thin,bottom_color white;pattern: pattern solid, fore_colour background_header")

        bold_center = xlwt.easyxf("font: bold on;align: horiz center,wrap on")
        
        worksheet.write(0,0,'Show Name',header)
        worksheet.write(0,1,'Show Number',header)
        worksheet.write(0,2,'Class Name',header)
        worksheet.write(0,3,'Class Number',header)
        worksheet.write(0,4,'Rider Name',header)
        worksheet.write(0,5,'Rider Number',header)
        worksheet.write(0,6,'Ride Number',header)
        worksheet.write(0,7,'By User',header)
        worksheet.write(0,8,'Token',header)
        worksheet.write(0,9,'Downloaded',header)
        worksheet.write(0, 10, 'Downloaded on', header)
        
        worksheet.col(0).width = 256 * 27
        worksheet.col(1).width = 256 * 12
        worksheet.col(2).width = 256 * 29
        worksheet.col(3).width = 256 * 12
        worksheet.col(4).width = 256 * 27
        worksheet.col(5).width = 256 * 12
        worksheet.col(6).width = 256 * 12
        worksheet.col(7).width = 256 * 15
        worksheet.col(8).width = 256 * 27
        worksheet.col(9).width = 256 * 14
        worksheet.col(10).width = 256 * 17

        row = 1
        for record in records:
            show_name = record.product_id.show_name
            show_number = record.product_id.show_number
            class_name = record.product_id.class_name
            class_number = record.product_id.class_number
            rider_name = record.product_id.rider_name
            rider_number = record.product_id.rider_number
            ride_number = record.product_id.ride_number
            user_name = record.partner_id.name
            token  = record.token
            downloaded = record.downloaded
            downloaded_on = self._format_date(record.downloaded_on) if record.downloaded_on else ''

            worksheet.write(row,0,show_name,align_left)
            worksheet.write(row,1,show_number,align_right)
            worksheet.write(row,2,class_name,align_left)
            worksheet.write(row,3,class_number,align_right)
            worksheet.write(row,4,rider_name,align_left)
            worksheet.write(row,5,rider_number,align_right)
            worksheet.write(row,6,ride_number,align_right)
            worksheet.write(row,6,ride_number,align_right)
            worksheet.write(row,7,user_name,align_left)
            worksheet.write(row, 8, token, align_left)
            worksheet.write(row, 9, downloaded, align_center)
            worksheet.write(row, 10,downloaded_on,align_right)

            row = row + 1
            
        now = datetime.strftime(datetime.now(),"%m-%d-%y")
        filename = 'Download_Data_Export_'+now+'.xls'
        response = request.make_response(None,
            headers=[('Content-Type', 'application/vnd.ms-excel'),
                    ('Content-Disposition', 'attachment; filename='+filename)])
        workbook.save(response.stream)

        return response 
        
        