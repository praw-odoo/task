from odoo import api,models,fields

class StockPickingType(models.Model):
    _inherit="stock.picking.type"

    add_lot_tmp_id = fields.Boolean(string="Show Add Bool Temp")