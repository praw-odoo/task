from odoo import http

class CallingCartUpdate(http.Controller):

    @http.route('/reorder', type='http', auth="user", website=True)
    def add_in_cart(self,**kwargs):
        old_order = http.request.env['sale.order'].browse(int(kwargs.get('order_id')))
        new_order = http.request.website.sale_get_order(force_create=True)
        # new_order.order_line.unlink()

        for line in old_order.order_line:
            new_order._cart_update(product_id=line.product_id.id, add_qty=line.product_uom_qty)

        return http.request.redirect('/my/orders')