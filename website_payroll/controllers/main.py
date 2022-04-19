from odoo import http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.http import Controller
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager, get_records_pager
class CustomerPortal(portal.CustomerPortal):
    
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id

        payslip = request.env['hr.payslip']
        employee_ids = request.env['hr.employee'].search(
            [('user_id', '=', request.env.user.id)]).ids
        if 'slip_count' in counters:
            values['slip_count'] = request.env['hr.payslip'].search_count([('employee_id', 'in', employee_ids)])\
                if payslip.check_access_rights('read', raise_exception=False) else 0
        return values

    def _prepare_portal_layout_values(self):
        """Values for /my/* templates rendering.

        Does not include the record counts.
        """
        payslip_user = False
        partner = request.env.user.partner_id
        if partner.user_id and not partner.user_id._is_public():
            payslip_user = partner.user_id

        return {
            'payslip_user': payslip_user,
            'page_name': 'home',
        }


    def _payslip_get_page_view_values(self, payslip, access_token, **kwargs):
        values = {
            'page_name': 'payslip',
            'payslip': payslip,
            'o':payslip
        }
        return self._get_page_view_values(payslip, access_token, values, 'my_payslip_history', False, **kwargs)

    def _prepare_payslips_domain(self, partner):
        return [
            ('state', 'in', ['draft', 'done', 'paid'])
        ]

    @http.route('/my/payslip',  type='http', auth="user", website=True)
    def portal_my_payslips(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        HrPayslip = request.env['hr.payslip']
        domain = self._prepare_payslips_domain(partner)
        if not sortby:
            sortby = 'date'
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        slip_count = HrPayslip.sudo().search_count([])
        pager = portal_pager(
            url="/my/payslip",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=slip_count,
            page=page,
        )
        # user_slips = request.uid
        # print("\n\n user_slips ",user_slips)
        employee_ids = request.env['hr.employee'].search(
            [('user_id', '=', request.env.user.id)]).ids
        # payslip = request.env['hr.payslip'].search(
        #     [('employee_id', 'in', employee_ids)])

        playslips = HrPayslip.search([('employee_id', 'in', employee_ids)])

        values = ({
            'date': date_begin,
            'playslips': playslips.sudo(),
            'page_name': 'slip',
            'pager': pager,
            'default_url': '/my/payslip',
            'sortby': sortby,
        })
        return request.render("website_payroll.portal_my_payslips",values)

    @http.route(['/my/payslip/<int:id>'], type='http', auth="public", website=True)
    def portal_my_payslip_detail(self, id, access_token=None, report_type=None, download=False, **kw):
        try:
            payslip_sudo = self._document_check_access('hr.payslip', id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=payslip_sudo, report_type=report_type, report_ref='hr_payroll.action_report_payslip', download=download)

        values = self._payslip_get_page_view_values(payslip_sudo, access_token, **kw)

        return request.render("website_payroll.payslip_template", values)