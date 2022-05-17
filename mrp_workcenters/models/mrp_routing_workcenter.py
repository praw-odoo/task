from odoo import api,models,fields

class MrpRoutingWorkcenter(models.Model):
    _inherit = "mrp.routing.workcenter"

    is_work_center_lock = fields.Boolean(string='Work Center Locked')
