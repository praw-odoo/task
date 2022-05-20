from odoo import api,models,fields

class MrpRoutingWorkcenter(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    location_ids = fields.Many2many('stock.location', string='Locations')
