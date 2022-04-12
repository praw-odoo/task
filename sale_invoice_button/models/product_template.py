from odoo import api, models, fields
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = "product.template"

    '''

    '''
    is_insurance = fields.Boolean()
    percent_cost_based_on = fields.Selection([
        ('TotalUn', 'Total Untaxed Amount'),
        ('Totaltx', 'Total taxed Amount')
    ])
    percent_applicable = fields.Float()

    @api.constrains('is_insurance')
    def _check_is_insurance(self):

        for product in self:
            if product.is_insurance and product.detailed_type != 'service':
                raise ValidationError(('You cannot apply insurance if product type is not service'))
