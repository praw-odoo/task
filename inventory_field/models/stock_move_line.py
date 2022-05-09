from odoo import api,models,fields

class StockMoveLine(models.Model):
    _inherit="stock.move.line"

    add_id = fields.Char(string="add")
    # print("\n\n add_lot_tmp_id",self.add_lot_tmp_id)
    # hideeee = fields.Boolean(string='Hide', compute="_compute_hide", default=False)

    # @api.depends('picking_type_id.add_lot_tmp_id')
    # def _compute_hide(self):
    #     print("\n\n cccccoooommpute")
    #     if self.picking_type_id.add_lot_tmp_id == False:
    #         print("\n\n falllllse")
    #         self.hideeee = False
    #     else:
    #         print("\n\n ttttrrrue")
    #         self.hideeee = True

    # @api.depends('picking_type_id.add_lot_tmp_id')
    # def _compute_add(self):
    #     print("\n\n cccccoooommpute")
    #     if self.picking_type_id.add_lot_tmp_id == False:
    #         print("\n\n falllllse")
    #         self.add_id = False
    #     else:
    #         print("\n\n ttttrrrue")
    #         self.add_id = True

# @api.onchange('picking_type_id.add_lot_tmp_id')
#     def _onchange_add(self):
#         print("\n\n cccccoooommpute")
#         if self.picking_type_id.add_lot_tmp_id == False:
#             print("\n\n falllllse")
#             self.add_id = False
#         else:
#             print("\n\n ttttrrrue")
#             self.add_id = True