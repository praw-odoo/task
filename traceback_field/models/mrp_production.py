from odoo import api, models, fields

class MrpProduction(models.Model):
    _inherit = "mrp.production"

    '''
    field declaration
    '''
    is_check = fields.Boolean()

    