from tracemalloc import DomainFilter
from odoo import api, models, fields

class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name:
            # Be sure name_search is symetric to name_get
            print("\n\n name : ",name)
            args = ['|',('name', operator, name),('mobile', operator, name)] + args
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)