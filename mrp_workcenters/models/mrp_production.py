from odoo import api, fields,models
from odoo.exceptions import UserError

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def button_plan(self):
        in_progress = self.env['mrp.production'].search([('state','=','progress')])
        # in_progress1 = self.env['mrp.production'].search([]).filtered(lambda mrp: mrp.state == 'progress')
        
        if self.bom_id.operation_ids.is_work_center_lock:
            if not in_progress:
                return super().button_plan()
            if any(order.product_id == self.product_id for order in in_progress):
                # if order.product_id == self.product_id:
                raise UserError("workcenter with default in progress")
            else:
                super().button_plan()
        else:
            super().button_plan()