from odoo import api, models, fields

class MrpProduction(models.Model):
    _inherit = "mrp.production"

    is_check = fields.Boolean()

    