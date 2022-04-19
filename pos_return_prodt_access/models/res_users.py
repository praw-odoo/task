from odoo import api,models,fields

class ResUsers(models.Model):
    _inherit="res.users"

    '''
    field declaration
    '''
    access_code = fields.Char(string="POS Return Access Code")