from odoo import models, fields,api

class PosConfig(models.Model):
    _inherit="pos.config"

    '''
    field declaration
    '''
    is_check = fields.Boolean(string="Enable Return with Access", readonly=False)
    access_users = fields.Many2many('res.users', string="POS return access users")