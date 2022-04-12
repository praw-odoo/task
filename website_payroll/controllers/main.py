

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
        # get customer sales rep
        sales_user = False
        partner = request.env.user.partner_id
        if partner.user_id and not partner.user_id._is_public():
            sales_user = partner.user_id

        return {
            'sales_user': sales_user,
            'page_name': 'home',
        }
    @http.route(['/my/payslip', '/my/payslip/page/<int:page>'],  type='http', auth="user", website=True)
    def portal_my_payslips(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        # values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        print("\n\n partner",partner)
        # HrPayslip = request.env['hr.payslip']
        # # if not sortby:
        # #     sortby = 'date'
        # if date_begin and date_end:
        #     domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        # slip_count = HrPayslip.search_count(domain)
        # pager = portal_pager(
        #     url="/my/orders",
        #     url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
        #     total=slip_count,
        #     page=page,
        #     step=self._items_per_page
        # )
        return request.render("website_payroll.portal_my_payslips")

        # values = self._prepare_portal_layout_values()
        # partner = request.env.user.partner_id
        # SaleOrder = request.env['sale.order']

        # domain = self._prepare_orders_domain(partner)

        # searchbar_sortings = self._get_sale_searchbar_sortings()

        # # default sortby order
        # if not sortby:
        #     sortby = 'date'
        # sort_order = searchbar_sortings[sortby]['order']

        # if date_begin and date_end:
        #     domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # # count for pager
        # order_count = SaleOrder.search_count(domain)
        # # pager
        # pager = portal_pager(
        #     url="/my/orders",
        #     url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
        #     total=order_count,
        #     page=page,
        #     step=self._items_per_page
        # )
        # # content according to pager
        # orders = SaleOrder.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        # request.session['my_orders_history'] = orders.ids[:100]

        # values.update({
        #     'date': date_begin,
        #     'orders': orders.sudo(),
        #     'page_name': 'order',
        #     'pager': pager,
        #     'default_url': '/my/orders',
        #     'searchbar_sortings': searchbar_sortings,
        #     'sortby': sortby,
        # })
        # return request.render("sale.portal_my_orders", values)