from odoo import api, models, fields

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    #secound_discount = fields.Many2one('sale.order', string='2nd Disc. %')
    secound_discount = fields.Float(string='2nd Disc. %')

    @api.onchange('discount','secound_discount','tax_id','price_unit','product_uom_qty')
    def _check_secound_discount(self):
        print("\n\n\n hello")
        #self.price_subtotal = self.price_subtotal - (self.price_subtotal*(self.discount/100))
        if self.secound_discount != 0:
            self.price_subtotal = self.price_subtotal - (self.price_subtotal*(self.secound_discount/100))
        else :
            self.price_subtotal = self.price_unit - (self.price_unit*(self.discount/100))