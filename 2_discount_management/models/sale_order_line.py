from optparse import Values
from odoo import api, models, fields

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    secound_discount = fields.Float(string='2nd Disc. %')

    @api.depends('state', 'price_reduce', 'product_id', 'untaxed_amount_invoiced', 'qty_delivered', 'product_uom_qty','secound_discount','price_subtotal')
    def _compute_amount(self):
        res = super()._compute_amount()
        for line in self:
            line.price_subtotal = line.price_subtotal - (line.price_subtotal*(line.secound_discount/100))
        return res


    def _prepare_invoice_line(self, **optional_values):
        values = super(SaleOrderLine, self)._prepare_invoice_line()
        values['secound_discount'] = self.secound_discount
        values['price_subtotal'] = self.price_subtotal
        return values

    # def _prepare_invoice_line(self, optional_values):

    #     values = super(SaleOrderLine, self)._prepare_invoice_line(optional_values)
    #     values['discount_2'] = self.discount_2
    #     print("\nvalue**",values)

    #     return values

    # @api.onchange('discount','secound_discount','tax_id','price_unit','product_uom_qty')
    # def _check_secound_discount(self):
    #     print("\n\n\n hello")
    #     if self.secound_discount != 0:
    #         self.price_subtotal = self.price_subtotal - (self.price_subtotal*(self.secound_discount/100))
    #     else :
    #         self.price_subtotal = self.price_unit - (self.price_unit*(self.discount/100))