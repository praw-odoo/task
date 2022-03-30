from odoo import models, fields,api

class ResConfigSetting(models.TransientModel):
    _inherit="res.config.settings"

    is_check = fields.Boolean(readonly=False)

    def set_values(self):
        res = super(ResConfigSetting, self).set_values()
        self.env['ir.config_parameter'].set_param('inventory_customization.is_check', self.is_check)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSetting, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        res.update(
            is_check= ICPSudo.get_param('inventory_customization.is_check'),
        )
        return res