from odoo import api,models,fields

class ProductPackaging(models.Model):
    _inherit = "product.packaging"

    comp_dict = {}
    @api.model
    def create(self, vals_list):
        res = super().create(vals_list)
        res.barcode = ''
        if res.package_type_id.auto_create_gtin:
            l = [s[0] for s in self.env.company.name.split()]
            for c in l:
                res.barcode = res.barcode + str(c)
            if not res.barcode in self.comp_dict:
                self.comp_dict[res.barcode] = 1
            else:
                self.comp_dict[res.barcode] += 1
            res.barcode = res.barcode + '/' + str(self.comp_dict[res.barcode])
            # str(self.env['ir.sequence'].next_by_code('pack.order'))
        return res