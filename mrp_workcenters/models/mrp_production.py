# from odoo import api, fields,models
# from odoo.exceptions import UserError

# class MrpProduction(models.Model):
#     _inherit = 'mrp.production'

#     def button_plan(self):
#         in_progress = self.env['mrp.production'].search([('state','=','progress')])
#         if any(workcenter.is_work_center_lock for workcenter in self.bom_id.operation_ids):
#             if not in_progress:
#                 return super().button_plan()
#             if any(order.product_id == self.product_id for order in in_progress):
#                 raise UserError("workcenter with default in progress")
#             else:
#                 super().button_plan()
#         else:
#             super().button_plan()Vishal Thacker (vst) — Today at 12:49 PM
from odoo import models
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def button_plan(self):
        if any(workorder.state == 'progress' for workorder in self.env["mrp.workorder"].search([('product_id', '=', self.product_id.id)])):
            raise UserError("Work center {} is locked for the operations".format(
                        [workcenter.name for workcenter in self.workorder_ids.search([('state', '=', 'progress')]).mapped('workcenter_id')]))
        return super().button_plan()
