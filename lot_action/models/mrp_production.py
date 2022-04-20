from odoo import api, models, fields

class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def lot_num(self):
        filtered_productions = self.filtered(lambda mo: mo.state == 'confirmed' and not mo.lot_producing_id)
        manufacturing_order_data = {}
        for product_id in filtered_productions.mapped('product_id').ids:
            for production in filtered_productions.filtered(
                    lambda mo: mo.product_id.id == product_id):
                if product_id in manufacturing_order_data.keys():
                    manufacturing_order_data[product_id].append(production)
                else:
                    manufacturing_order_data[product_id] = [production]
        for k in manufacturing_order_data.keys():  
            flag = 1
            ans = 0
            for value in manufacturing_order_data[k]:
                if flag == 1:
                    value.action_generate_serial()
                    ans = value.lot_producing_id
                    flag = flag + 1 
                else:
                    value.lot_producing_id = ans