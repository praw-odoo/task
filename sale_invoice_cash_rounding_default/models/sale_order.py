from odoo import models,fields
import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"
    invoice_cash_rounding_id = fields.Many2one('account.cash.rounding', string='Cash Rounding Method',
        help='Defines the smallest coinage of the currency that can be used to pay by cash.')

    def _create_invoices(self, grouped=False, final=False, date=None):
        moves = super()._create_invoices(grouped=grouped, final=final, date=date)
        invoice_cash_rounding_id = self.invoice_cash_rounding_id.id
        # self.env['ir.default'].get_model_defaults('account.move',condition='move_type=out_invoice').get('invoice_cash_rounding_id')
        print("\n\n invoice_cash_rounding_id",invoice_cash_rounding_id)
        if invoice_cash_rounding_id:
            moves.update({
                'invoice_cash_rounding_id': invoice_cash_rounding_id
            })
            # Update invoice lines, otherwise rounding line will not be created properly
            moves.filtered(lambda r: r.state == "draft").with_context(check_move_validity=False)._move_autocomplete_invoice_lines_values()
        return moves
