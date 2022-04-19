from odoo import models, fields,api

class ResConfigSetting(models.TransientModel):
    _inherit="res.config.settings"

    '''
    field declaration
    '''
    is_check = fields.Boolean(string="Enable Return with Access", readonly=False)
    access_users = fields.Many2many('res.users', string="POS return access users")

    def set_values(self):
        res = super(ResConfigSetting, self).set_values()
        self.env['ir.config_parameter'].set_param('pos_return_prodt_access.is_check', self.is_check)
        self.env['ir.config_parameter'].set_param('pos_return_prodt_access.access_users', self.access_users)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSetting, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        res.update(
            is_check= ICPSudo.get_param('pos_return_prodt_access.is_check'),
            access_users= ICPSudo.get_param('pos_return_prodt_access.access_users'),
        )
        return res