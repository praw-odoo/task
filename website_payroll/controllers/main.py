
from odoo import http
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
            # ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['draft', 'done', 'paid'])
        ]

    @http.route(['/my/payslip', '/my/payslip/page/<int:page>'],  type='http', auth="user", website=True)
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
            # step=self._items_per_page
        )

        slips = HrPayslip.sudo().search([])
        # request.session['my_orders_history'] = orders.ids[:100]

        values = ({
            'date': date_begin,
            'orders': slips.sudo(),
            'page_name': 'slip',
            'pager': pager,
            'default_url': '/my/payslip',
            # 'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("website_payroll.portal_my_payslips",values)


        # searchbar_sortings = self._get_sale_searchbar_sortings()

        # sort_order = searchbar_sortings[sortby]['order']

        # if date_begin and date_end:
        #     domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # return request.render("sale.portal_my_orders", values)