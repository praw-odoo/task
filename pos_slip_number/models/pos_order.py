from odoo import api,models,fields

class PosOrder(models.Model):
    _inherit = "pos.order"

    sequence_num = fields.Char('Order Reference', required=True, index=True, copy=False, default='New')

    @api.model
    def create(self, vals):
        vals['sequence_num'] = self.env['ir.sequence'].next_by_code('sequence.order')
        print("\n\n\n sequence_num : ",vals['sequence_num'])
        return super(PosOrder, self).create(vals)