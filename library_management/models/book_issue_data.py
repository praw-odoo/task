# -- coding: utf-8 --

from odoo import api, models, fields
from odoo.exceptions import UserError, ValidationError
import datetime


class BookIssueData(models.Model):
    _name = 'book.issuedata'
    _description = "Book Issue Data"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # ==========================
    # Field Declaration
    # ==========================

    name = fields.Char(string='Student Name', related='user_ids.name')
    book_name = fields.Many2one(comodel_name='product.template', domain=[('available_books', '>', 0)])
    mobile_number = fields.Char(string='Student Mobile Number', related='user_ids.mobile')
    type_of = fields.Selection(related='user_ids.member_id.type_of', string="Type", default='student')
    user_ids = fields.Many2one(comodel_name='res.users', string="User")
    username_of_student = fields.Char(related='user_ids.member_ref')
    book_details = fields.Char(string="Book ISBN No.", related='book_name.isbn')
    date = fields.Date(default=lambda self: fields.Datetime.now())
    book_return = fields.Date(compute='book_return_date', store=True)
    book_return_day = fields.Integer(compute='book_return_days')
    book_fine = fields.Integer(compute='compute_book_fine')
    renew_times = fields.Integer(default=0)

    # ==========================
    # Method Declaration
    # ==========================

    # def issue_book(self, user=False, book=False, **kw):
# 
        # books_limit = {'staff': 20, 'student': 3, 'gm': 2, 'gml': 4}
        # total_issued_books = self.env['book.issuedata'].search_count([('user_ids', '=', user.id)])
        # domain = [('isbn', '!=', None), ('available_books', '>', 0),
                #   ('book_purchase_ids', 'not in', user.member_id.ids)]
        # books_can_be_issued = self.env['product.template'].search(domain).ids
        # if total_issued_books < (
                # books_limit.get(user.member_id.type_of) or 0) and user and book and book.id in books_can_be_issued:
            # vals = {
                # 'user_ids': user.id,
                # 'date': datetime.now(),
                # 'book_name': book.id
            # }
            # self.env['book.issuedata'].sudo().create(vals)
            # book.book_purchase_ids += user.member_id
            # return self.redirect('/mybooks')
        # else:
            # raise UserError('You exceeded your book issued limit or you already have that.')
# 
    @api.depends('date')
    def book_return_date(self):
        for date in self:
            if date.type_of == 'student':
                date.book_return = date.date + datetime.timedelta(days=14)
            elif date.type_of == 'staff':
                date.book_return = date.date + datetime.timedelta(days=25)
            elif date.type_of == 'gm' or date.type_of == 'glm':
                date.book_return = date.date + datetime.timedelta(days=30)

    @api.depends('book_return')
    def book_return_days(self):
        for days in self:
            day = days.book_return - datetime.date.today()
            days.book_return_day = day.days

    @api.depends('book_return')
    def compute_book_fine(self):
        for days in self:
            day = days.book_return - datetime.date.today()
            fine_day = day.days
            if fine_day < 0:
                days.book_fine = fine_day * -1
            else:
                days.book_fine = 0

    @api.model_create_multi
    def create(self, vals_list):
        result = super().create(vals_list)
        mail_template = self.env.ref('library_management.book_issued_email')
        for rec in result:
            mail_template.send_mail(rec.id, force_send=True)
        return result
    
    # def issue_book(self):
        # pass
    # #     seq_obj = self.env["ir.sequence"]
    #     for rec in self:
    #         if (rec.card_id.end_date < self.date and
    #                 rec.card_id.end_date > self.date):
    #             raise UserError(_("The Membership of library card is over!"))
    #         code_issue = seq_obj.next_by_code("library.book.issue") or _("New"
    #                                                                      )
    #         if (rec.name and rec.name.availability == "notavailable" and
    #                 not rec.name.is_ebook):
    #             raise UserError(_(
    #                 "The book you have selected is not available. Please try after sometime!"))
    #         if rec.student_id:
    #             issue_str = ""
    #             for book in rec.search([("card_id", "=", rec.card_id.id),
    #                                     ("state", "=", "fine")]):
    #                 issue_str += str(book.issue_code) + ", "
    #                 raise UserError(_(
    #                     """You can not request for a book until the fine is not paid for book issues %s!""") % issue_str)
    #         if rec.card_id:
    #             card_rec = rec.search_count([("card_id", "=", rec.card_id.id),
    #                                          ("state", "in", ["issue", "reissue"])])
    #             if rec.card_id.book_limit > card_rec:
    #                 return_day = rec.name.day_to_return_book
    #                 rec.write({"state": "issue",
    #                            "day_to_return_book": return_day,
    #                            "issue_code": code_issue})
    #         return True

    # def return_book(self):
        # pass

