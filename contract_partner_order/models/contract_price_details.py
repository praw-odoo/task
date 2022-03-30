
from odoo import api, models, fields

class ContractPriceDetails(models.Model):
    _name = "contract.price.details"

    '''
    field declaration
    '''
    partner_id = fields.Many2one('res.partner')
    date_from = fields.Date()
    date_to = fields.Date()
    contract_price = fields.Float()
    product_id = fields.Many2one('product.template')