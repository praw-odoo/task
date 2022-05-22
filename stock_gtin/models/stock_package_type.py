from odoo import api,models,fields

class StockPackageType(models.Model):
    _inherit = "stock.package.type"

    auto_create_gtin = fields.Boolean(string='Auto-Create GTIN')
