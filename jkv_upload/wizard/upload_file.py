# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Copyright (C) 2015 Novobi LLC (<http://novobi.com>)
#
##############################################################################
import csv
from odoo import api, fields, models

class Import(models.TransientModel):
    _name = 'jkv_upload.import'

    file = fields.Binary('File', help="File to check and/or import, raw binary (not base64)")
    filename = fields.Char()
    
    @api.multi
    def _read_csv(self, options):
        csv_data = self.file

        # TODO: guess encoding with chardet? Or https://github.com/aadsm/jschardet
        encoding = options.get('encoding', 'utf-8')
        if encoding != 'utf-8':
            # csv module expect utf-8, see http://docs.python.org/2/library/csv.html
            csv_data = csv_data.decode(encoding).encode('utf-8')

        csv_iterator = csv.reader(
            StringIO(csv_data),
            quotechar=str(options['quoting']),
            delimiter=str(options['separator']))

        return (
            [item.decode('utf-8') for item in row]
            for row in csv_iterator
            if any(x for x in row if x.strip())
        )