from odoo import http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.http import Controller
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager, get_records_pager

class CustomerPortal(Controller):
    
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

    def _prepare_payslips_domain(self, partner):
        return [
            ('state', 'in', ['draft', 'done', 'paid'])
        ]

    @http.route(['/my/payslip','/my/payslip/page/<int:page>'],  type='http', auth="user", website=True)
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

        playslips = HrPayslip.search([])

        values = ({
            'date': date_begin,
            'playslips': playslips.sudo(),
            'page_name': 'slip',
            'pager': pager,
            'default_url': '/my/payslip',
            'sortby': sortby,
        })
        return request.render("website_payroll.portal_my_payslips",values)

    @http.route(['/my/payslip/<int:payslip_id>'], type='http', auth="public", website=True)
    def portal_my_payslip_detail(self, payslip_id, access_token=None, report_type=None, download=False, **kw):
        print("\n\n hello****************----------------")
        try:
            payslip_sudo = self._document_check_access('account.move', payslip_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=payslip_sudo, report_type=report_type, report_ref='account.account_invoices', download=download)

        values = self._invoice_get_page_view_values(payslip_sudo, access_token, **kw)
        return request.render("hr_payroll.portal_invoice_page", values)

    # @http.route(['/my/payslip_id/<int:id>'], type='http', auth="public", website=True)
    # def portal_payslip_page(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        # return {
        #     'name': 'Payslip',
        #     'type': 'ir.actions.act_ # @http.route(['/my/payslip_id/<int:id>'], type='http', auth="public", website=True)
    # def purl',
        #     'url': '/print/payslips?list_ids=%(list_ids)s' % {'list_ids': ','.join(str(x) for x in kw.)},
        # }


        # return {
        #     "name": "Debug Payslip",
        #     "type": "ir.actions.act_url",
        #     "url": "/debug/payslip/%s" % kw.get(id),
        # }












        # print("\n\n\n idddddddddddddddddddddddd : ",kw,type(kw))
        # values = self._prepare_portal_layout_values()
        # partner = request.env.user.partner_id
        # HrPayslip = request.env['hr.payslip']
        # domain = self._prepare_payslips_domain(partner)
        # if not sortby:
        #     sortby = 'date'
        # if date_begin and date_end:
        #     domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        # slip_count = HrPayslip.sudo().search_count([])
        # pager = portal_pager(
        #     url="/my/payslip",
        #     url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
        #     total=slip_count,
        #     page=page,
        # )
        # user_values = HrPayslip.browse(kw.get('id'))
        # # user_values = self.env['hr.payslip'].browse(self.env.context['kw'])
        # # user_values = self.env['hr.payslip'].browse(self._context.get('kw'))
        # print("\n\n recoooooord",user_values.net_wage)
        # playslips = HrPayslip.search([])

        # values = ({
        #     'date': date_begin,
        #     'playslips': playslips.sudo(),
        #     'page_name': 'slip',
        #     'pager': pager,
        #     'default_url': '/my/payslip',
        #     'sortby': sortby,
        #     'partner': partner,
        #     'list_ids': user_values
        # })
        # # print("idddddddddddddddddddddddd",playslips.id)
        # return request.render("hr_payroll.report_payslip",values)   
