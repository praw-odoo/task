from odoo import api, models, fields

class ResPartner(models.Model):
    _inherit = "res.partner"

    contract_ids = fields.One2many('contract.price.details','partner_id', readonly=False)