from odoo import api, models, fields

class ResPartner(models.Model):
    _inherit = "res.partner"

    '''
    field declaration
    '''    
    contract_ids = fields.One2many('contract.price.details','partner_id', string="Contract ids", readonly=False)
