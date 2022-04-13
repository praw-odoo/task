from os import name
from odoo import api, models, fields
from datetime import datetime

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def birthday_wishes(self):
        '''
        this method helps to find employees whose birthday is today and sends mail to that 
        employees for wishing birthday
        '''
        employee_ids = self.search([('birthday','=',datetime.today())])
        
        for employee in employee_ids:
            mail_template = self.env.ref('birthday_wishes_cron.email_template')
            mail_template.send_mail(employee.id, force_send=True)