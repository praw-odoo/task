from odoo import api,models,fields

class ResPartner(models.Model):
    _inherit = "res.partner"

    '''
    field declaration
    '''
    product_detail_list_ids = fields.One2many(string="Product Detail List ids", comodel_name='product.list', inverse_name="partner_id", string="Product Uom")
