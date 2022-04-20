from odoo import api, models, fields

class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def lot_num(self):
        """
        The lot_num function is used to generate a lot number for the manufacturing order.
        It takes in an argument of a list of manufacturing orders and returns the lot number
        for each one. It does this by first checking if there is already a serial tracked on 
        the product, then it checks if there are any confirmed manufacturing orders with that 
        product id, then it checks if all those confirmed manufacturing orders have been assigned 
        a serial number yet, and finally it assigns the next available serial to each one.
        """
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