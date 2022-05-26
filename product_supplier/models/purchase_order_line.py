from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order.line'

    @api.model
    def create(self,vals):
        res = super().create(vals)
        min_qty_ext = self.env['product.supplierinfo'].search([('name','=',res.order_id.partner_id.id),('product_tmpl_id','=',res.product_id.product_tmpl_id.id)]).minimum_qty
        if min_qty_ext:
            res.product_qty = min_qty_ext
        return res