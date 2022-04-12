from odoo import api, models, fields

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    '''
    field declaration
    '''
    secound_discount = fields.Float(string="2 disc")

    def _get_price_total_and_subtotal_model(self, price_unit, quantity, discount, currency, product, partner, taxes, move_type):
        '''
        this method applies 2 discount on price_Subtotal
        '''
        res = super()._get_price_total_and_subtotal_model(price_unit, quantity, discount, currency, product, partner, taxes, move_type)
        price_subtotal = res.get('price_subtotal') - ((res.get('price_subtotal')*self.secound_discount)/100)
        res.update({'price_subtotal': price_subtotal})
        return res

    @api.onchange('secound_discount')
    def _onchange_secound_discount(self):
        '''
        this method updates price_Subtotal when 2 discount changes
        '''
        self.price_subtotal = self.price_subtotal -((self.price_subtotal*self.secound_discount)/100)
