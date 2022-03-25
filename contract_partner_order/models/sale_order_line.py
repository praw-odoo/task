from datetime import datetime
from odoo import api, models, fields

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange('product_id')
    def product_id_change(self):
        res = super().product_id_change()
        last_cont = len(self.order_id.partner_id.contract_ids.filtered(lambda x: x.product_id))
        st_dt = self.order_id.partner_id.contract_ids[last_cont-1].date_from
        end_dt = self.order_id.partner_id.contract_ids[last_cont-1].date_to
        for contract in self.order_id.partner_id.contract_ids.filtered(lambda x: x.product_id.id==self.product_id.product_tmpl_id.id and st_dt >= datetime.today().date() or end_dt <= datetime.today().date()):
            self.price_unit = contract.contract_price
            print("\n\n self.price_unit",self.price_unit)
            print("\n\n",contract.contract_price)
        return res

        
    #  print("\n\n res",res)
    #     aa = self.order_id.partner_id.contract_ids.filtered(lambda x: x.product_id.id==self.product_id.product_tmpl_id.id and x.date_from >= datetime.today().date() or x.date <= datetime.today().date())
    #     print("\n\n aaaaaaaaaaa====", aa)
    #     yyyy
    #     # self.price_unit = contract.contract_price
