# -- coding: utf-8 --

from odoo import api, models, fields
from odoo.osv import expression


class ResUsers(models.Model):
    _inherit = 'res.users'

    member_id = fields.Many2one(comodel_name='members.registration', string="Member")
    member_ref = fields.Char(related="member_id.user_ids", string="Member Reference")

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        user_ids = []
        if operator not in expression.NEGATIVE_TERM_OPERATORS:
            if operator == 'ilike' and not (name or '').strip():
                domain = [('member_ref', 'ilike', name)]
            else:
                domain = ['|', ('login', '=', name), ('member_ref', 'ilike', name)]
            user_ids = self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
        if not user_ids:
            user_ids = self._search(
                expression.AND([['|', ('name', operator, name), ('member_ref', 'ilike', name)], args]), limit=limit,
                access_rights_uid=name_get_uid)
        return user_ids