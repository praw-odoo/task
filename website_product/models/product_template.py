from odoo import api,models,fields

class ProductTemplate(models.Model):
    _inherit = "product.template"

    courses = fields.Many2one('slide.channel')