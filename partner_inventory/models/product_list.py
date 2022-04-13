from odoo import api, models, fields


class ProductList(models.Model):
    _name="product.list"
    _description = "productlist"

    '''
    field declaration
    '''
    product_id = fields.Many2one("product.product", string="Product id")
    uom_id = fields.Many2one("uom.uom", string="Uom id", domain="[('category_id','=',uom_category)]")
    partner_id = fields.Many2one("res.partner", string="Partner id")
    uom_category = fields.Many2one(string="Uom Category", related="product_id.uom_id.category_id")