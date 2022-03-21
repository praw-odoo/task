from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    @api.model
    def create(self,vals):
        res = super(ProductTemplate, self).create(vals)
        if res.categ_id.assign_sequence == True :
            res.default_code = res.categ_id.seq_id.next_by_id()
        elif res.categ_id.parent_id.seq_id:
            res.default_code = res.categ_id.parent_id.seq_id.next_by_id()
        return res