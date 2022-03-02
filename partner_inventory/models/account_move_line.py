from odoo import api, fields, models

class  AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # @api.onchange('product_id')
    # def  _onchange_product_id(self):
    #     print("\n\n\n\ aaa")
    #     res = super(). _onchange_product_id()
    #     for line in self:
    #         if line.order_id.partner_id:
    #             if line.order_id.partner_id.product_detail_list_ids:
    #                 uom_details_ids = line.order_id.partner_id.product_detail_list_ids
    #                 for record in uom_details_ids:
    #                     if line.product_id == record.product_id:
    #                         line.product_uom_id = record.uom_id
    #     return res

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super()._onchange_product_id()
        if self.product_id and self.partner_id:
            self.product_uom_id = self.partner_id.product_detail_list_ids.filtered(lambda x : x.product_id.id == self.product_id.id).uom_id.id
        return res