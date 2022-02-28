from odoo import api, fields, models


class resPartner(models.Model):
    _inherit="res.partner"

    days_to_deliver = fields.Integer(string="Days to Deliver")
