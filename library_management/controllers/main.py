from odoo import http
from odoo.http import request
from datetime import datetime
from odoo.exceptions import UserError


class website(http.Controller):
    @http.route('/registraion', website=True)
    def registration_form(self, **kw):
        check_user = request.env['members.registration'].search([])
        if check_user:
            for i in check_user:
                if i.username_of_student == request.env.user.name:
                    return request.redirect('books')
            return request.render('library_management.regisration_form_template')
        else:
            return request.render('library_management.regisration_form_template')

    @http.route('/books', website=True)
    def avb_books(self, search_string=False, **kw):
        domain = [('isbn', '!=', None), ('name', 'ilike', search_string),
        ('available_books', '>', 0), ('book_purchase_ids', 'not in', request.env.user.member_id.ids)]
        books = request.env['product.template'].sudo().search(domain)
        return request.render('library_management.book_details_template', {'books': books})

    @http.route('/book_details/<int:book>', auth="public", website=True)
    def property(self, book=False, **kw):
        book = request.env['product.template'].browse(book)
        if book:
            return request.render('library_management.book_details', {
                'book': book, 'user': request.env.user
            })

    @http.route('/issue/<model("product.template"):book>/<model("res.users"):user>', auth="public",
                website=True)
    def issue_book(self, user=False, book=False, **kw):

        books_limit = {'staff': 20, 'student': 3, 'gm': 2, 'gml': 4}
        total_issued_books = request.env['book.issuedata'].search_count([('user_ids', '=', user.id)])
        domain = [('isbn', '!=', None), ('available_books', '>', 0),
                  ('book_purchase_ids', 'not in', user.member_id.ids)]
        books_can_be_issued = request.env['product.template'].search(domain).ids
        if total_issued_books < (
                books_limit.get(user.member_id.type_of) or 0) and user and book and book.id in books_can_be_issued:
            vals = {
                'user_ids': user.id,
                'date': datetime.now(),
                'book_name': book.id
            }
            request.env['book.issuedata'].sudo().create(vals)
            book.book_purchase_ids += user.member_id
            return request.redirect('/mybooks')
        else:
            raise UserError('You exceeded your book issued limit or you already have that.')

    @http.route('/mybooks', auth="public", website=True)
    def my_books(self, **kw):
        my_book = request.env['book.issuedata'].search([('user_ids', '=', request.env.user.id)])
        print('?' * 100, my_book, request.env.user, request.env['book.issuedata'].search([]).mapped('user_ids'))
        return request.render('library_management.my_issue_books', {'mybook': my_book})

    @http.route('/myprofile', auth="public", website=True)
    def my_profile(self, **kw):
        my_profile_details = request.env['members.registration'].search(
            [('username_of_student', '=', request.env.user.name)])
        my_issue_books = request.env['book.issuedata'].search([('username_of_student', '=', request.env.user.name)])
        my_request_books = request.env['book.request'].search([('requested_by', '=', request.env.user.name)])
        if my_profile_details:
            return request.render('library_management.my_profile_details',
                                  {'my_profile_details': my_profile_details, 'issue': len(my_issue_books),
                                   'request_book': len(my_request_books)})
        else:
            return request.render('library_management.regisration_form_template')

    @http.route('/requestbook', website=True)
    def request_book(self, **kw):
        check_user = request.env['members.registration'].search([])
        for i in check_user:
            if i.username_of_student == request.env.user.name:
                return request.render('library_management.request_books')
        return request.render('library_management.request_books')

    @http.route('/request_book', website=True)
    def req_book(self, **kw):
        request.env['book.request'].sudo().create(kw)
        return request.redirect('requestbook')

    @http.route('/myrequestbook', auth="public", website=True)
    def my_request_books(self, **kw):
        my_request_ = request.env['book.request'].search([('requested_by', '=', request.env.user.name)])
        return request.render('library_management.my_request_books', {'myrequest': my_request_})

    @http.route('/renewbook/<model("book.issuedata"):renew>')
    def renew_book(self, renew=False, **kw):
        if renew and renew.renew_times < 2:
            renew.date = datetime.now()
            renew.renew_times += 1
            return request.redirect('/mybooks')

    @http.route('/retuenbook/<model("book.issuedata"):returnbook>')
    def return_book(self, returnbook=False, **kw):
        if returnbook:
            returnbook.book_name.book_purchase_ids -= request.env.user.member_id
            returnbook.unlink()
            return request.redirect('/mybooks')
