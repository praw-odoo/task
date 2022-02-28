from odoo import api, fields, models


class ResPartnerNOD(models.Model):
    _inherit = "res.partner"

    number_of_days = fields.Integer(string="Number of Days")
