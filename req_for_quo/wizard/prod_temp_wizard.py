from datetime import date, datetime
from odoo import api, models, fields
from odoo.exceptions import UserError


class ProdTemp(models.TransientModel):
    _name = "prod.temp"

    """
    field declaration
    """
    quantity = fields.Float(string="Quantity", default=1)
    unit_of_measure_id = fields.Many2one("uom.uom", string="Unit of Measure")
    scheduled_date = fields.Datetime(string="Scheduled Date", default=datetime.now())

    # method to get default value of uom
    @api.model
    def default_get(self, fields):
        """
        this method helps to get default uom from product.template
        """
        active_id = self._context.get("active_id")
        res = super(ProdTemp, self).default_get(fields)
        uom_id = self.env["product.template"].browse(active_id).uom_po_id.id
        res["unit_of_measure_id"] = uom_id
        return res

    # method for creating request for quotation
    def request_for_quotation(self):
        """
        this method create request for quotation from the values from wizard
        """
        active_id = self._context.get("active_id")
        product = self.env["product.template"].browse(active_id)
        product_supplierinfo_id = product.product_variant_id._select_seller(
            quantity=self.quantity,
            uom_id=self.unit_of_measure_id,
            date=self.scheduled_date,
        )
        if product_supplierinfo_id:
            val_list = {
                "partner_id": product_supplierinfo_id.name.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.product_variant_ids.id,
                            "name": product.name,
                            "product_qty": self.quantity,
                            "product_uom": self.unit_of_measure_id.id,
                        },
                    )
                ],
            }
            self.env["purchase.order"].create(val_list)
        else:
            raise UserError(
                (
                    "There is no Vendor define for this Product : "
                    + product.product_variant_ids.name
                    + " Please define Vendor first"
                )
            )
