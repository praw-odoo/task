from odoo import api,models,fields

class PosOrder(models.Model):
    _inherit = "pos.order"

    postcode = fields.Char(related='partner_id.zip')