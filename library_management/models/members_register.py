# -- coding: utf-8 --

from odoo import api, models, fields


class MembersRegistration(models.Model):
    _name = "members.registration"
    _description = "Members Registration"
    _rec_name = "name"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # ==========================
    # Field Declaration
    # ==========================

    name = fields.Char(string='Name', required=True)
    Email_id = fields.Char(string='Email Id', required=True)
    mobile_number = fields.Char(string='Mobile Number')
    type_of = fields.Selection([
        ('student', 'Student'),
        ('staff', 'Staff'),
        ('gm', 'General Member'),
        ('glm', 'General Life Member'),

    ], string="Type", required=True)
    user_ids = fields.Char(string="Member Reference", required=True)
    username_of_student = fields.Char(default=lambda self: self.env.user.name)
