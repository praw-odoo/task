from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = "product.category"

    '''
    field declaration
    '''
    assign_sequence = fields.Boolean(string="Assign Seq")
    seq_id = fields.Many2one("ir.sequence", string="Seq id")
