# -- coding: utf-8 --

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class BookStock(models.Model):
    _inherit = "product.template"
    _description = "Book Details"
    _sql_constraints = [('unique_isbn_number', 'unique(isbn)', 'Enter Unique ISBN Number')]

    # ==========================
    # Field Declaration
    # ==========================

    book_name = fields.Char()
    book_author_ids = fields.Many2many('book.author', required=False)
    department_id = fields.Many2one('book.department', required=True)
    isbn = fields.Char("ISBN Code", unique=True, required=True, help="Shows International Standard Book Number")
    fine_lost = fields.Float("Fine Lost", compute='_total_fine_lost', help="Enter fine lost")
    fine_late_return = fields.Float("Fine Amount If Late Return (Per Day)", help="Enter late return", default="1")
    return_day = fields.Integer("Return Days", default=14, readonly=True)
    book_purchase_ids = fields.Many2many('members.registration', 'name')
    total_book_copy = fields.Integer(string="Total Book Copy", default=0, required=True)
    total_issue_book = fields.Integer(compute='_find_total_issue_book', string="Total Issue Book", default=0)
    available_books = fields.Integer(compute='_find_available_book', string="available Books", default=0, store=True)

    # ==========================
    # Method Declaration
    # ==========================

    def write(self, vals):
        res = super(BookStock, self).write(vals)
        if len(self.isbn) != 13:
            raise ValidationError("ISBN must be 13 charecter")
        else:
            return res

    @api.depends('book_purchase_ids')
    def _find_total_issue_book(self):
        for rec in self:
            rec.total_issue_book = len(rec.book_purchase_ids)

    @api.depends('total_issue_book', 'total_book_copy')
    def _find_available_book(self):
        for rec in self:
            rec.available_books = rec.total_book_copy - rec.total_issue_book

    @api.depends('standard_price')
    def _total_fine_lost(self):
        for rec in self:
            rec.fine_lost = rec.standard_price // 2
