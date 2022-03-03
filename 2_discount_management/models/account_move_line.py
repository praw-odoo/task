from odoo import api, models, fields

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    #secound_discount = fields.Many2one('sale.order', string='2nd Disc. %')
    secound_discount = fields.Float(string='2nd Disc. %')

    @api.depends('sale_id.discount','sale_id.secound_discount')
    #@api.depends('sale_id')
    def _compute_discount(self):
        self.secound_discount = self.sale_id.discount
        self.secound_discount = self.sale_id.secound_discount
