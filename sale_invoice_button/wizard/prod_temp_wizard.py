from datetime import date, datetime
from odoo import api, models, fields
from odoo.exceptions import UserError


class ProdTemp(models.TransientModel):
    _name = "prod.temp"

    """
    field declaration
    """
    move_id = fields.Many2one("account.move", string="Invoice")
    product_id = fields.Many2one("product.template", string="Product",
    domain="[('is_insurance', '=', True)]" )
    insurance = fields.Float(string="Tax %", compute="_compute_insurance")

    @api.depends("product_id")
    def _compute_insurance(self):
        for record in self:
            record.insurance = record.product_id.percent_applicable

    # method for creating request for quotation
    def request_for_invocing(self):
        """
        this method create add product from the wizard
        """

        val_list = {
            "product_id": self.product_id.id,
            "name": self.product_id.name,
            "quantity": 1,
            "product_uom_id": self.product_id.uom_id.id,
            "account_id": self.move_id.journal_id.default_account_id.id,
            'tax_ids' : self.product_id.taxes_id,
            "price_unit": self.product_id.percent_applicable,
            "move_id": self.move_id.id,
            # "price_subtotal" : self.product_id.percent_applicable
        }
        # chk = 0
        # for move in self.move_id:
        #     for line in move.line_ids:
        #         if line.debit and chk != 1:
        #             try:
        #                 line.debit = line.debit + self.product_id.percent_applicable
        #                 chk = chk +1
        #             except:
        #                 self.env["account.move.line"].create(val_list)
        #                 print("\n\nAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAa",line.debit)
        # print("\n\n\n self.move_id.debit",self.record.move_id.line_ids.debit)
        # self.move_id.invoice_line_ids.debit = self.move_id.invoice_line_ids.debit + self.product_id.percent_applicable
        self.move_id._validate_taxes_country()
        self.env["account.move.line"].create(val_list)
