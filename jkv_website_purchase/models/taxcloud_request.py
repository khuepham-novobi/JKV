# -*- coding: utf-8 -*-
from odoo.addons.sale_account_taxcloud.models.taxcloud_request import TaxCloudRequest
import requests
import logging

class TaxCloudRequest(TaxCloudRequest):
    
    def verify_address(self, partner):
        zip5 = ''
        zip4 = ''
        partner_zip = partner.zip
        if partner_zip.find('-') != -1:
            zip_code = partner_zip.split('-')
            zip_code_5 = str(zip_code[0])
            zip_code4 = str(zip_code[1])
            zip5 = [int(s) for s in zip_code_5.split() if s.isdigit()]
            zip5 = zip5[0]
            zip4 = [int(s) for s in zip_code4.split() if s.isdigit()]
            zip4 = zip4[0]
            #logging.info("ZIP")
            #logging.info(zip5)
            #logging.info(zip4)
        else:
            zip_code_5 = str(partner_zip)
            zip5 = [int(s) for s in zip_code_5.split() if s.isdigit()]
            zip5 = zip5[0]
            #logging.info("ZIP")
            #logging.info(zip5)
        address_to_verify = {
            'apiLoginID': self.api_login_id,
            'apiKey': self.api_key,
            'Address1': partner.street or '',
            'Address2': partner.street2 or '',
            'City': partner.city,
            "State": partner.state_id.code,
            "Zip5": zip5,
            "Zip4": zip4
        }
        res = requests.post("https://api.taxcloud.com/1.0/TaxCloud/VerifyAddress", data=address_to_verify).json()
        if int(res.get('ErrNumber', False)):
            # If VerifyAddress fails, use Lookup with the initial address
            res.update(address_to_verify)
        return res