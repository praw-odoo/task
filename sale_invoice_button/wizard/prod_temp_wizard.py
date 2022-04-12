from datetime import date, datetime
from odoo import api, models, fields
from odoo.exceptions import UserError


class ProdTemp(models.TransientModel):
    _name = "prod.temp"

    """
    field declaration
    """
    move_id = fields.Many2one("account.move", string="Invoice")
    product_id = fields.Many2one(
        "product.template", domain="[('is_insurance', '=', True)]"
    )
    insurance = fields.Float(compute="_compute_insurance")

    @api.depends("product_id")
    def _compute_insurance(self):
        for record in self:
            record.insurance = record.product_id.percent_applicable

    # method for creating request for quotation
    def request_for_invocing(self):
        """
        this method create request for quotation from the values from wizard
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
        }
        self.env["account.move.line"].create(val_list)
