from tracemalloc import DomainFilter
from odoo import api, models, fields

class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        """
        The _name_search function tries to match the mobile 
         to the
        record's name or reference.  It returns all records matching a
        case-insensitive search for any words in `search_string`, while also
        taking into account the full name and reference of each record.  This is
        usually enough to find what you're looking for, without having to enter a
        full email address.
        """
        args = args or []
        if name:
            # Be sure name_search is symetric to name_get
            print("\n\n name : ",name)
            args = ['|',('name', operator, name),('mobile', operator, name)] + args
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)