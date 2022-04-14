from odoo import models

class HrPayslip(models.Model):
    _name="hr.payslip"
    _inherit = ['portal.mixin','hr.payslip']