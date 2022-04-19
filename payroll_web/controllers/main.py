
from odoo import http,fields
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.tools.translate import _
from odoo.addons.portal.controllers.portal import CustomerPortal
# from odoo.addons.portal.controllers.portal import pager as portal_pager


class CustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id

        payslip = request.env['hr.payslip']
        if 'payslip_count' in counters:
            values['payslip_count'] = payslip.search_count([]) \
                if payslip.check_access_rights('read', raise_exception=False) else 0
        return values

    @http.route(['/my/payslips', '/my/payslips/page/<int:page>'], type='http', auth="user", website=True)
    def hr_payroll_portal_inherit(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        "payslipe is view in website"
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        payslip = request.env['hr.payslip'].search([])

        values.update({
            'payslip': payslip.sudo(),
            'page_name': 'slip',
            'date': date_begin,
            'default_url': '/my/payslips',
        })
        return http.request.render('payroll_web.hr_payroll_portal_inherit', values)

    def _payslip_get_page_view_values(self, pay, access_token, **kwargs):
        values = {
            'page_name': 'payslip',
            'payslip': pay,
            'o':pay,
        }
        return self._get_page_view_values(pay, access_token, values, 'my_payslip_history', False, **kwargs)

    @http.route(['/my/payslips/<int:id>'], type='http', auth="public", website=True)
    def portal_order_page(self, id, report_type=None, access_token=None, message=False, download=False, **kw):
        try:
            payslip_sudo = self._document_check_access(
                'hr.payslip', id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=payslip_sudo, report_type=report_type, report_ref='hr_payroll.action_report_payslip', download=download)
        values = self._payslip_get_page_view_values(
            payslip_sudo, access_token, **kw)
        print("\n\n value is fiend:::::::;;;;;;;", values)
        # return request.render('hr_payroll.report_payslip', values)
        return request.render('payroll_web.payslip_portal_template', values)

