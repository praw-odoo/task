from odoo import _, api, fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    '''
    field declaration
    '''
    zero_stock_approval = fields.Boolean(string='Appoval')

    def _approval(self):
        """
        The _approval function is a helper function that is used to determine whether 
        or not the current user is the same as the parent_id. If they are, then it 
        returns True, otherwise False.
        """
        if self.env.uid == self.parent_id.user_id.id:
            self.zero_stock_approval = True