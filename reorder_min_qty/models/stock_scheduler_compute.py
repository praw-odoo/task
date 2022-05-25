from odoo import models, fields


class StockSchedulerCompute(models.TransientModel):
    _inherit = 'stock.scheduler.compute'

    # val = fields.One2many('stock.warehouse.orderpoint','get')

    # def procure_calculation(self):
    #     print("\n\n val",self.val)
    #     for order in self.val:
    #         print("\n\n order",order)