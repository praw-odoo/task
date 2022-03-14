from odoo import api, fields, models

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _prepare_picking(self):
        values = super()._prepare_picking()
        print("\n\n sdfghjkdfghjkldfghjk",values)
        values['origin'] = self.name + "(" + self.partner_ref + ")"
        print("\n\n ert6yuioptyuiop",values['origin'])
        return values