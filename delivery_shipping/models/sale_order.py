from odoo import api, fields, models
import datetime

class SaleOrder(models.Model):
    _inherit="sale.order"

    '''
    field declaration
    '''
    appointment_date = fields.Datetime(string="Appointment Date")
    commitment_date = fields.Datetime(readonly=False, string="Commitment Date", compute='commute_commitment_date')

    @api.depends("appointment_date")
    def commute_commitment_date(self):
        '''
        commitment date calculated from appoinment date and days to dilver
        '''
        for record in self:
            if record.appointment_date and record.partner_id.days_to_deliver > 0 :
                record.commitment_date = record.appointment_date - datetime.timedelta(days=record.partner_id.days_to_deliver)

    def action_confirm(self):
        '''
        this method helps to assign appointment_date from stock.picking
        '''
        record = super(SaleOrder, self).action_confirm()
        for data in self.picking_ids:
            data.appointment_date = self.appointment_date
        return record
