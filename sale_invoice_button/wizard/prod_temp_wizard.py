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
        "product.template", string="Product", domain="[('is_insurance', '=', True)]"
    )
    insurance = fields.Float(string="Tax %", compute="_compute_insurance")

    @api.depends("product_id")
    def _compute_insurance(self):
        for record in self:

            record.insurance = (
                record.product_id.percent_applicable * self.move_id.amount_untaxed
            )

    # method for creating request for quotation
    def request_for_invocing(self):
        """
        this method add product from the wizard
        """
        taxes = self.product_id.taxes_id.filtered(
            lambda tax: tax.company_id == self.move_id.company_id
        )
        if taxes and self.move_id.fiscal_position_id:
            taxes = self.move_id.fiscal_position_id.map_tax(taxes)
        print("\n\n\n taxes ", taxes.id)
        val_list = {
            "invoice_line_ids": [
                (0,0,{
                        "product_id": self.product_id.id,
                        "name": self.product_id.name,
                        "quantity": 1,
                        "product_uom_id": self.product_id.uom_id.id,
                        "account_id": self.move_id.journal_id.default_account_id.id,
                        "tax_ids": taxes.ids,
                        "price_unit": self.insurance,
                        "move_id": self.move_id.id,
                    },
                )
            ],
        }

        self.move_id.write(val_list)
