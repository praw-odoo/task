from odoo import api, models, fields
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = "product.template"

    '''
    field declaration
    '''
    is_insurance = fields.Boolean(string="Insurance")
    percent_cost_based_on = fields.Selection([
        ('TotalUn', 'Total Untaxed Amount'),
        ('Totaltx', 'Total taxed Amount')
    ], string="Type of Tax")
    percent_applicable = fields.Float(string="Tax %")

    @api.constrains('is_insurance')
    def _check_is_insurance(self):
        '''
        check if type of product is not service then could not apply insurance
        '''
        for product in self:
            if product.is_insurance and product.detailed_type != 'service':
                raise ValidationError(('You cannot apply insurance if product type is not service'))
