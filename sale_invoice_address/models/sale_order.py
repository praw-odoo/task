# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        super().onchange_partner_id()
        self.partner_invoice_id = self.partner_id.child_ids.filtered(lambda p: p.type == 'invoice' and p.is_default).sorted(lambda p : p.name)[0]
        self.partner_shipping_id = self.partner_id.child_ids.filtered(lambda p: p.type == 'delivery' and p.is_default).sorted(lambda p : p.name)[0]