from odoo import api, fields, models
import datetime

class StockPicking(models.Model):
    _inherit="stock.picking"

    '''
    field declaration
    '''
    appointment_date = fields.Datetime(string="Appointment Date", compute="_compute_appointment_date", readonly=False)

    @api.depends('sale_id', 'partner_id')
    def _compute_appointment_date(self):
        '''
        this method helps to assign appointment_date from sale order
        '''
        self.appointment_date = self.sale_id.appointment_date

    @api.depends('appointment_date' , 'sale_id')
    def _compute_scheduled_date(self):
        '''
        this method helps to calculate scheduled date from appointment date and number of days
        '''
        if self.appointment_date:
            self.scheduled_date = self.appointment_date - datetime.timedelta(days=self.partner_id.number_of_days)
        else:
            self.scheduled_date = self.create_date
