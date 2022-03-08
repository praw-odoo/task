from optparse import Values
from odoo import api, models, fields

class AccountMove(models.Model):
    _inherit = "account.move"
    
   
    # def _get_price_total_and_subtotal(self, price_unit=None, quantity=None, discount=None, currency=None, product=None, partner=None, taxes=None, move_type=None):
    #     print("\n\n hello \n\n")
    #     res = super()._get_price_total_and_subtotal()
    #     self.ensure_one()
    #     return self._get_price_total_and_subtotal_model(
    #         price_subtotal = self.price_subtotal - ((self.price_subtotal*self.line_ids.secound_discount)/100)
    #         )

    def _set_price_and_tax_after_fpos(self):
        print("\n\n hello \n\n")
        res = super()._set_price_and_tax_after_fpos()
        self.ensure_one()
        if price_subtotal:
            price_subtotal = self.price_subtotal - ((self.price_subtotal*self.line_ids.secound_discount)/100)
        return res