from odoo import models
from odoo.exceptions import UserError

class StockScrap(models.Model):
    _inherit = "stock.scrap"

    def action_validate(self):
        print("\n\n hello ",self.env['ir.config_parameter'].sudo().get_param('is_check'))
        if not self.env['ir.config_parameter'].sudo().get_param('inventory_customization.is_check'):
            raise UserError(("User Group cannot add followers"))
        return super().action_validate()