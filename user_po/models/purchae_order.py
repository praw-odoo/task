from odoo import api, fields, models

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _prepare_picking(self):
        val = super()._prepare_picking()
        val['log_user_id'] = self.user_id.id
        return val