from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_delivery_methods(self):
        print("\n\n\n   inside _get_delivery_methods")
        address = self.partner_shipping_id
        if self.partner_id.property_delivery_carrier_id:
            return self.env['delivery.carrier'].sudo().search(['|',('website_published', '=', True),
                ('id', '=', self.partner_id.property_delivery_carrier_id.id)]).available_carriers(address)
        else:
            return self.env['delivery.carrier'].sudo().search([('website_published', '=', True)]).available_carriers(address)
