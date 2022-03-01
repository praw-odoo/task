from odoo import api,models,fields

class ResPartner(models.Model):
    _inherit = "res.partner"

    product_detail_list_ids = fields.One2many(comodel_name='product.list', inverse_name="partner_id", string="Product Uom")
