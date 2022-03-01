from odoo import api, models, fields


class ProductList(models.Model):
    _name="product.list"
    _description = "productlist"

    product_id = fields.Many2one("product.product")
    uom_id = fields.Many2one("uom.uom", domain="[('category_id','=',uom_category)]")
    partner_id = fields.Many2one("res.partner")
    uom_category = fields.Many2one(related="product_id.uom_id.category_id")