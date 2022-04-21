from odoo import api, fields, models

class StockPicking(models.Model):
    _inherit = "stock.picking"

    log_user_id = fields.Many2one('res.users', string="Purchase Representative")
