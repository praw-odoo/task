from odoo import api, fields, models

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _prepare_picking(self):
        '''
        this method helps to send to send the value of origin
        '''
        values = super()._prepare_picking()
        values['origin'] = self.name + "(" + self.partner_ref + ")"
        return values