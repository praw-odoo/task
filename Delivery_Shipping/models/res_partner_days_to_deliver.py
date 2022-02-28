from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit="res.partner"

    days_to_deliver = fields.Integer(string="Days to Deliver")
