from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    def _quantity_in_progress(self):
        res = super()._quantity_in_progress()
        print("\n\n res",res)
        return res
    
    def _prepare_procurement_values(self, date=False, group=False):
        res = super()._prepare_procurement_values()
        # min_qty_ext = self.env["product.supplierinfo"].search([("name","in",proc_values["orderpoint_id"].product_id.seller_ids.name.ids),("product_tmpl_id","=",proc_values["orderpoint_id"].product_id.product_tmpl_id.id)]).minimum_qty
        for supp in res["orderpoint_id"].product_id.seller_ids:
            min_qty_req = self.env["product.supplierinfo"].search([("name","=",supp.name.id),("product_tmpl_id","=",res["orderpoint_id"].product_id.product_tmpl_id.id)])[0].minimum_qty
            if min_qty_req:
                res["orderpoint_id"]["qty_to_order"] = min_qty_req
        return res