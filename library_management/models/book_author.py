# -- coding: utf-8 --

from odoo import models, fields


class BookAuthor(models.Model):
    _name = 'book.author'
    _description = 'Book Author'
    _sql_constraints = [('unique_author_name', 'unique(name)', 'Author cannot be duplicate ')]

    # ==========================
    # Field Declaration
    # ==========================

    name = fields.Char(string='Author Name', required=True)
    color = fields.Integer()
