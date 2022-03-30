from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = "res.partner"

    '''
    field declaration
    ''' 
    to_confirm = fields.Boolean()