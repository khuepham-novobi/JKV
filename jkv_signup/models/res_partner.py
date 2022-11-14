# -*- coding: utf-8 -*-
from operator import itemgetter

from odoo import api, fields, models,  _
from datetime import datetime
from odoo.osv import expression
import logging


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    partner_id = fields.Many2one(required=False)
    partner_invoice_id = fields.Many2one(required=False)
    partner_shipping_id = fields.Many2one(required=False)

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    alias_name = fields.Char(string='Alias name')
    receive_email = fields.Boolean(string='Receive via Email')
    mapping_partner_ids = fields.Many2many('res.partner', relation='rel_jkv_mapping_partners', column1='partner_source', column2='partner_des', string='Mapping Partners')
    mapping_videos = fields.Many2many('product.template', relation='rel_jkv_mapping_video',string='JKV Videos', column1='partner_video_source', column2='partner_video_des',compute='_mapping_videos', store=False)
    show_ids = fields.Many2many('jkv.show.venue',string='Shows',store=False,compute='_get_shows')
    rider_ids = fields.One2many('jkv.rider','rider_id',string='Riders')
    mapping_riders = fields.Many2many('jkv.rider', string='Rider', compute='_mapping_riders', store=True)
    horse_name = fields.Char(string='Horse Name',store=False,compute='_get_horse',search='_search_horse_name')
    is_rider = fields.Boolean(string='Is Rider', default=False)
    is_trainer = fields.Boolean(string='Is Trainer', default=False)
    is_owner = fields.Boolean(string='Is Owner', default=False)


    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('alias_name', operator, name), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        partners = self.search(domain + args, limit=limit)
        return partners.name_get()

    @api.depends(
        'mapping_partner_ids', 
        'mapping_partner_ids.jkv_video_rider_ids', 
        'mapping_partner_ids.jkv_video_trainer_ids', 
        'mapping_partner_ids.jkv_video_owner_ids',
        'jkv_video_rider_ids',
        'jkv_video_trainer_ids',
        'jkv_video_owner_ids'
    )
    def _mapping_videos(self):
        query = """
SELECT pt.id
FROM product_template pt
    LEFT JOIN jkv_filename jf ON jf.id = pt.filename_id
    LEFT JOIN jkv_rider jr ON jr.id = jf.rider_id
WHERE jr.owner_id IN %s
    OR jr.trainer_id IN %s
    OR jr.rider_id IN %s
    OR jr.rider_2nd_id IN %s
        """
        for record in self:
            partner_ids = tuple(set(record.mapping_partner_ids.ids + [record.id]))
            self.env.cr.execute(query, (partner_ids,) * 4)
            ids = self.env.cr.fetchall()
            video_ids = map(itemgetter(0), ids)
            record.update(dict(mapping_videos=[(6, 0, video_ids)]))

    def _get_horse(self):
        for record in self:
            horse_name = ' '
            for e in record.mapping_videos:
                if e.horse_name:
                    horse_name = horse_name + ',' + e.horse_name
            record.horse_name = horse_name

    def _search_horse_name(self, operator, value):
        records = self.env['jkv.rider'].sudo().search([('horse_name',operator,value)])
        ids = []
        for record in records:
            ids.append(record.rider_id.id)
            ids.append(record.trainer_id.id)
            ids.append(record.owner_id.id)
            ids.extend(record.rider_id.mapping_partner_ids._ids)
            ids.extend(record.trainer_id.mapping_partner_ids._ids)
            ids.extend(record.owner_id.mapping_partner_ids._ids)
        return [('id', 'in', ids)]

    def _get_shows(self):
        for record in self:
            show_ids = []               
            for e in record.mapping_videos:
                if e.filename_id:
                    show_ids.append((4,e.filename_id.show_id.id))
                    
            record.show_ids = show_ids

    @api.depends('mapping_partner_ids','rider_ids')
    def _mapping_riders(self):
        for record in self:
            for rider in record.rider_ids:
                record.mapping_riders = [(4,rider.id)]           
            for partner in record.mapping_partner_ids:
                for rider in partner.rider_ids:
                    record.mapping_riders = [(4,rider.id)]