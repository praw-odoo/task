from odoo import api, models, fields

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    
    
    secound_discount = fields.Float(string='2nd Disc. %')
    #secound_discount = fields.Many2one('sale.order.line', string='2nd Disc. %', related='invoice_lines.secound_discount')

    # @api.depends('secound_discount')
    # def _compute_secound_discount(self):
    #     print("\n\n\n hello")
    #     self.secound_discount = self.secound_discount