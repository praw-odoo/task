from odoo import models,_


class HrPayslip(models.Model):
    _name = 'hr.payslip'
    _inherit = ['portal.mixin','hr.payslip']

    # type_name = fields.Char('Type Name', compute='_compute_type_name')
    # partner_id = fields.Many2one('res.partner', string='Partner')
    # user_id = fields.Many2one('res.users')

    # def _get_portal_return_action(self):
    #     """ Return the action used to display orders when returning from customer portal. """
    #     self.ensure_one()
    #     return self.env.ref('sale.action_quotations_with_onboarding')



    # def _compute_type_name(self):
    #     for record in self:
    #         record.type_name = _('Payslip') if record.state in ('draft', 'sent', 'cancel') else _('Pay Slip')

    def _get_report_base_filename(self):
        return "{} - {}".format(("Payslip"), self.number)

    def _compute_access_url(self):
        super()._compute_access_url()
        for record in self:
            record.access_url = "/my/payslips/%s" % (record.id)
