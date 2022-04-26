from odoo import api, fields, models

class StockBackorderConfirmation(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        res['log_user_id'] = self.pick_ids.log_user_id.id
        return res