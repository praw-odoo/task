from odoo import api, models, fields

class ResPartner(models.Model):
    _inherit = "res.partner"

    def name_get(self):
        """
        The name_get function returns a tuple containing the name and and the field we want
        to append
        """
        result = []    	
        for rec in self:
            result.append((rec.id, '%s [ %s ]' % (rec.name,rec.zip)))
        return result