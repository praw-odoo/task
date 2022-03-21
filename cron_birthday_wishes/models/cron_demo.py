from odoo import api, models, fields
from datetime import datetime

class CronDemo(models.Model):
    _name = "cron.demo"

    current_date = fields.Date(default=datetime.today())
    
    def birthday_wishes(self):
        print("\n\n***********@@@@@@@@@@ happy birthday @@@@@@@@@@***********\n\n")
        print("\n\n self : ",self)
        for record in self:
            if self.current_date == self.env['hr.employee'].browse(record.birthday):
                print("\n\n hello \n\n")