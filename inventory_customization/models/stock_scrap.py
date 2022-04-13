from odoo import models
from odoo.exceptions import UserError

class StockScrap(models.Model):
    _inherit = "stock.scrap"

    def action_validate(self):
        if not self.env['ir.config_parameter'].sudo().get_param('inventory_customization.is_check'):
            raise UserError(("User Group cannot add followers"))
        return super().action_validate()