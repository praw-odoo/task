from odoo import fields, models

class ResPartner(models.Model):
    _inherit = "res.partner"

    '''
    field declaration
    ''' 
    to_confirm = fields.Boolean(string="To Confirm")