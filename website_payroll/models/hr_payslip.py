from odoo import models

class HrPayslip(models.Model):
    _name="hr.payslip"
    _inherit = ['portal.mixin','hr.payslip']

    def _get_report_base_filename(self):
        return "{} - {}".format(("Payslip"), self.number)

    def _compute_access_url(self):
        super()._compute_access_url()
        for record in self:
            record.access_url = "/my/payslip/%s" % (record.id)