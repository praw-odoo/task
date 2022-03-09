from odoo import api, models, fields

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    
    secound_discount = fields.Float(string='2nd Disc. %')

    def _get_price_total_and_subtotal_model(self, price_unit, quantity, discount, currency, product, partner, taxes, move_type):
        
        res = super()._get_price_total_and_subtotal_model(price_unit, quantity, discount, currency, product, partner, taxes, move_type)
        price_subtotal = res.get('price_subtotal') - ((res.get('price_subtotal')*self.secound_discount)/100)
        res.update({'price_subtotal': price_subtotal    })
        return res

    @api.onchange('secound_discount')
    def _onchange_secound_discount(self):
        print("\n\n in onchange")
        self.price_subtotal = self.price_subtotal -((self.price_subtotal*self.secound_discount)/100)
