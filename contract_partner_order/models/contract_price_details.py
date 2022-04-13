
from odoo import api, models, fields

class ContractPriceDetails(models.Model):
    _name = "contract.price.details"

    '''
    field declaration
    '''
    partner_id = fields.Many2one('res.partner', string="Partner id")
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    contract_price = fields.Float(string="Contract Price")
    product_id = fields.Many2one('product.template', string="Product id")