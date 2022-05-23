from odoo import _,api,models,fields

class ProductPackaging(models.Model):
    _inherit = "product.packaging"
    # sequence_id = fields.Many2one(
        # 'ir.sequence', 'Reference Sequence',
        # check_company=True, copy=False)

    # comp_dict = {}
    @api.model
    def create(self, vals_list):
        res = super().create(vals_list)
        if res.package_type_id.auto_create_gtin:
            res.barcode = self.env['ir.sequence'].next_by_code('pack.order')
        return res
        
        # .sudo()
        # 
        # 
        # .create({
                    # 'name': _('Pack Order') + ' ',
                    # 'prefix': str(self.env.company) + '/' , 'padding': 5,
                # }).id
        
        # self.env['ir.sequence'].sudo().create({
                    # 'name': '00',
                    # 'prefix': self.env['ir.sequence'].next_by_code('pack.order'),
                    # 'company_id': vals_list.get('company_id') or self.env.company.id,
                # }).id
        # 
        
        
        # self.env['ir.sequence'].with_company(self.company_id).next_by_code('pack.order')
    
        # if res.package_type_id.auto_create_gtin:
        #     IrSequence = self.env['ir.sequence'].with_company(self.company_id)
        #     res.barcode = IrSequence.next_by_code('pack.order')
        #     # self.env['ir.sequence'].with_company(self.env.company).next_by_code('pack.order')
        #     if not res.barcode:
        #         IrSequence.sudo().create({
        #     'name': 'Colombian electronic invoicing sequence for company %s' % invoice.company_id.id,
        #     'code': seq_code,
        #     'implementation': 'no_gap',
        #     'padding': 10,
        #     'number_increment': 1,
        #     'company_id': self.company_id.id,
        #     })
            # res.barcode = IrSequence.next_by_code(pack.order)
        return res









    # def create(self, vals_list):
    #     res = super().create(vals_list)
    #     res.barcode = ''
    #     if res.package_type_id.auto_create_gtin:
    #         l = [s[0] for s in self.env.company.name.split()]
    #         for c in l:
    #             res.barcode = res.barcode + str(c)
    #         if not res.barcode in self.comp_dict:
    #             self.comp_dict[res.barcode] = 1
    #         else:
    #             self.comp_dict[res.barcode] += 1
    #         res.barcode = res.barcode + '/' + str(self.comp_dict[res.barcode])
    #         # str(self.env['ir.sequence'].next_by_code('pack.order'))
    #     return res