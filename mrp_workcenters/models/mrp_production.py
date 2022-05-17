from odoo import api, fields,models
from odoo.exceptions import UserError

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def button_plan(self):
        if self.bom_id.operation_ids.is_work_center_lock:
            for line in self.workorder_ids.workcenter_id:    
                if self.bom_id.operation_ids.workcenter_id == line:
                        super().button_plan()
                else:
                    raise UserError("Alternative workcenter cannot produce until Work Center is Locked")
        else:
            super().button_plan()