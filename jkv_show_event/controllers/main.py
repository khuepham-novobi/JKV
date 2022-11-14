# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import ast
from datetime import datetime
try:
    import xlwt
except ImportError:
    xlwt = None
   
class Export(http.Controller):

        
    @http.route('/customer_record/export', type='http', auth='user')
    def export_customer_records (self,record_ids,**kwargs):
    
        workbook = xlwt.Workbook()
        ids = ast.literal_eval(record_ids)
        records = request.env['res.partner'].sudo().browse(ids)
        
        worksheet = workbook.add_sheet("Sheet1",cell_overwrite_ok=True)
        
        xlwt.add_palette_colour("background_header", 0x23)
        workbook.set_colour_RGB(0x23, 195, 134, 71)
        
        bold = xlwt.easyxf("font: bold on;")
        align_right = xlwt.easyxf("align: horiz right")
        align_left = xlwt.easyxf("align: horiz left")
        
        align_center = xlwt.easyxf("align: horiz center,wrap on")
        header = xlwt.easyxf("font: bold on,colour white;align: horiz center,wrap on;borders:bottom thin,bottom_color white;pattern: pattern solid, fore_colour background_header")

        bold_center = xlwt.easyxf("font: bold on;align: horiz center,wrap on")

        worksheet.write(0, 0, 'First Name', header)
        worksheet.write(0, 1, 'Last Name', header)
        worksheet.write(0, 2, 'Street', header)
        worksheet.write(0, 3, 'City', header)
        worksheet.write(0, 4, 'State', header)
        worksheet.write(0, 5, 'Zip', header)
        worksheet.write(0, 6, 'Phone', header)
        worksheet.write(0, 7, 'Email', header)
        worksheet.write(0, 8, 'USEF Number', header)
        worksheet.write(0, 9, 'Type', header)
        worksheet.write(0, 10, 'Receive via Email', header)

        worksheet.col(0).width = 256 * 15
        worksheet.col(1).width = 256 * 15
        worksheet.col(2).width = 256 * 35
        worksheet.col(3).width = 256 * 18
        worksheet.col(4).width = 256 * 18
        worksheet.col(5).width = 256 * 8
        worksheet.col(6).width = 256 * 17
        worksheet.col(7).width = 256 * 25
        worksheet.col(8).width = 256 * 15
        worksheet.col(9).width = 256 * 20
        worksheet.col(10).width = 256 * 20

        row = 1
        for record in records:
            first_name = record.jkv_first_name
            last_name = record.jkv_last_name
            street = record.street if record.street else ''
            city = record.city if record.city else ''
            state = record.state_id.name if record.state_id else ''
            zip = record.zip if record.zip else ''
            phone = record.phone if record.phone else ''
            email = record.email if record.email else ''
            jkv_customer_usef_number = record.jkv_customer_usef_number if record.jkv_customer_usef_number else ''
            type = ''
            if record.is_rider:
                type = 'Rider'
            if record.is_trainer:
                type = type + ' - Trainer' if type else 'Trainer'
            if record.is_owner:
                type = type + ' - Owner' if type else 'Owner'

            worksheet.write(row, 0, first_name, align_left)
            worksheet.write(row, 1, last_name, align_left)
            worksheet.write(row, 2, street, align_left)
            worksheet.write(row, 3, city, align_left)
            worksheet.write(row, 4, state, align_left)
            worksheet.write(row, 5, zip, align_right)
            worksheet.write(row, 6, phone, align_right)
            worksheet.write(row, 7, email, align_left)
            worksheet.write(row, 8, jkv_customer_usef_number, align_right)
            worksheet.write(row, 9, type, align_left)
            worksheet.write(row, 10, record.receive_email, align_center)

            row = row + 1
            
        now = datetime.strftime(datetime.now(),"%m-%d-%y")
        filename = 'Customer_Data_Export_'+now+'.xls'
        response = request.make_response(None,
            headers=[('Content-Type', 'application/vnd.ms-excel'),
                    ('Content-Disposition', 'attachment; filename='+filename)])
        workbook.save(response.stream)

        return response 

        