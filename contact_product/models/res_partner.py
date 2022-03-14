from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = "res.partner"
    
    @api.model
    def create(self,vals):
        if vals.get('customer_rank') >= 1:
            vals['ref'] = self.env['ir.sequence'].next_by_code('customer.sequence')
        elif vals.get('supplier_rank') >= 1:
            vals['ref'] = self.env['ir.sequence'].next_by_code('supplier.sequence')
        return super(ResPartner, self).create(vals)
