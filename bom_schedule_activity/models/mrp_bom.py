from odoo import models

class MrpBom(models.Model):
    _name="mrp.bom"
    _inherit = ['mail.thread', 'mail.activity.mixin','mrp.bom']