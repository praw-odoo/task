from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    def _prepare_procurement_values(self, date=False, group=False):
        proc_values = super()._prepare_procurement_values()
        min_qty_ext = self.env['product.supplierinfo'].search([('name','in',proc_values["orderpoint_id"].product_id.seller_ids.name.ids),('product_tmpl_id','=',proc_values["orderpoint_id"].product_id.product_tmpl_id.id)]).minimum_qty
        proc_values["orderpoint_id"]["qty_to_order"] = min_qty_ext
        return proc_values

        # ('name','=',proc_values["orderpoint_id"].product_id.seller_ids.id),