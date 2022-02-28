from odoo import api, fields, models
import datetime

class StockPicking(models.Model):
    _inherit="stock.picking"

    appointment_date = fields.Datetime(string="Appointment Date",related='sale_id.appointment_date', compute="_compute_appointment_date", readonly=False)

    @api.depends('sale_id', 'partner_id')
    def _compute_appointment_date(self):
        self.appointment_date = self.sale_id.appointment_date

    @api.depends('appointment_date' , 'sale_id')
    def _compute_scheduled_date(self):
        if self.appointment_date:
            self.scheduled_date = self.appointment_date - datetime.timedelta(days=self.partner_id.number_of_days)
        else:
            self.scheduled_date = self.create_date
