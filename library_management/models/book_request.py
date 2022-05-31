# -- coding: utf-8 --

from odoo import models, fields
from odoo.exceptions import UserError, ValidationError


class BookRequest(models.Model):
    _name = "book.request"
    _description = "Book Request"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # ==========================
    # Field Declaration
    # ==========================

    book_name = fields.Char(required=True)
    _rec_name = "book_name"
    book_author = fields.Char(required=True)
    edition = fields.Char(required=True)
    publisher = fields.Char()
    requested_by = fields.Char(default=lambda self: self.env.user.name)
    request_date = fields.Date(default=lambda self: fields.Datetime.now(), copy=False)

    status = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('inprocess', 'In Process')], default='draft')
