from odoo import api, models, fields

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    '''
    field declaration
    '''
    secound_discount = fields.Float(string='2nd Disc. %')

    @api.depends('state', 'price_reduce', 'product_id', 'untaxed_amount_invoiced', 'qty_delivered', 'product_uom_qty','secound_discount','price_subtotal')
    def _compute_amount(self):
        '''
        this method applies 2 discount on price_Subtotal
        '''
        res = super()._compute_amount()
        for line in self:
            line.price_subtotal = line.price_subtotal - (line.price_subtotal*(line.secound_discount/100))
        return res


    def _prepare_invoice_line(self, **optional_values):
        '''
        this method sends secound_discount from sale.order.line to account.move.line
        '''
        values = super(SaleOrderLine, self)._prepare_invoice_line()
        values['secound_discount'] = self.secound_discount
        return values