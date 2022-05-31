# -- coding: utf-8 --

from odoo import models, fields


class BookDepartment(models.Model):
    _name = "book.department"
    _description = "Book department"

    # ==========================
    # Field Declaration
    # ==========================

    name = fields.Char(string='Department Name', required=True)
