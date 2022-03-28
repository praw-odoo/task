from odoo.http import request
from odoo.tools.json import scriptsafe as json_scriptsafe

class callingMaethod(object):
    # def sale_get_order(self, force_create=False, code=None, update_pricelist=False, force_pricelist=False):
    #     print("\n\n sale_get_order in inherit")
    #     res = super().sale_get_order(force_create=False, code=None, update_pricelist=False, force_pricelist=False)
    #     return res.sale_order
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        print("\n\n hello 1")
        sale_order = request.website.sale_get_order(force_create=True)
        if sale_order.state != 'draft':
            request.session['sale_order_id'] = None
            sale_order = request.website.sale_get_order(force_create=True)

        product_custom_attribute_values = None
        if kw.get('product_custom_attribute_values'):
            product_custom_attribute_values = json_scriptsafe.loads(kw.get('product_custom_attribute_values'))

        no_variant_attribute_values = None
        if kw.get('no_variant_attribute_values'):
            no_variant_attribute_values = json_scriptsafe.loads(kw.get('no_variant_attribute_values'))

        sale_order._cart_update(
            product_id=int(product_id),
            add_qty=add_qty,
            set_qty=set_qty,
            product_custom_attribute_values=product_custom_attribute_values,
            no_variant_attribute_values=no_variant_attribute_values
        )
        print("\n\n hello 2")
        if kw.get('express'):
            return request.redirect("/shop/checkout?express=1")

        return request.redirect("/shop/cart")