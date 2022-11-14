# -*- coding: utf-8 -*-
from odoo import api, models


class JKVShowVenue(models.Model):
    _inherit = 'jkv.show.venue'

    @api.multi
    def unlink(self):
        """
        This method will delete all sale orders that don't have any order line
        This will also delete all filename which is in the shows but not yet been purchased
        """
        show_product_videos = self.env['product.template'].sudo().search([('filename_id.show_id.id', 'in', self.ids)])
        show_filenames = self.env['jkv.filename'].sudo().search([('show_id.id', 'in', self.ids)])
        product_ids = show_product_videos.mapped('product_variant_id.id')
        sale_lines = self.env['sale.order.line'].sudo().search([('product_id.id', 'in', product_ids)])
        invoice_lines = self.env['account.invoice.line'].sudo().search([('product_id.id', 'in', product_ids)])

        product_video = self.env.ref('jkv_delete.product_video')
        sale_lines.write({'product_id': product_video.id})
        invoice_lines.write({'product_id': product_video.id})

        show_filenames.with_context(product_remove=True).unlink()
        show_product_videos.with_context(video_remove=True, skip_detaching_product=True).unlink()

        res = super(JKVShowVenue, self).unlink()
        return res
