from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def create(self,vals):
        res = super().create(vals)

        if res.partner_id == res.