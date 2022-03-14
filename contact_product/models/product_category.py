from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = "product.category"
    
    assign_sequence = fields.Boolean()
    seq_id = fields.Many2one("ir.sequence")
