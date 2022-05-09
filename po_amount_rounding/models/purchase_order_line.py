# class AccountMoveLine(models.Model):
#     _name = "account.move.line"
#     _description = "Journal Item"
#     _order = "date desc, move_name desc, id"
#     _check_company_auto = True

#     # ==== Business fields ====
#     move_id = fields.Many2one('account.move', string='Journal Entry',
#         index=True, required=True, readonly=True, auto_join=True, ondelete="cascade",
#         check_company=True,
#         help="The move of this entry line.")
#     move_name = fields.Char(string='Number', related='move_id.name', store=True, index=True)
#     date = fields.Date(related='move_id.date', store=True, readonly=True, index=True, copy=False, group_operator='min')
#     ref = fields.Char(related='move_id.ref', store=True, copy=False, index=True, readonly=True)
#     parent_state = fields.Selection(related='move_id.state', store=True, readonly=True)
#     journal_id = fields.Many2one(related='move_id.journal_id', store=True, index=True, copy=False)
#     company_id = fields.Many2one(related='move_id.company_id', store=True, readonly=True)
#     company_currency_id = fields.Many2one(related='company_id.currency_id', string='Company Currency',
#         readonly=True, store=True,
#         help='Utility field to express amount currency')
#     account_id = fields.Many2one('account.account', string='Account',
#         index=True, ondelete="cascade",
#         domain="[('deprecated', '=', False), ('company_id', '=', 'company_id'),('is_off_balance', '=', False)]",
#         check_company=True,
#         tracking=True)
#     account_internal_type = fields.Selection(related='account_id.user_type_id.type', string="Internal Type", readonly=True)
#     account_internal_group = fields.Selection(related='account_id.user_type_id.internal_group', string="Internal Group", readonly=True)
#     account_root_id = fields.Many2one(related='account_id.root_id', string="Account Root", store=True, readonly=True)
#     sequence = fields.Integer(default=10)
#     name = fields.Char(string='Label', tracking=True)
#     quantity = fields.Float(string='Quantity',
#         default=1.0, digits='Product Unit of Measure',
#         help="The optional quantity expressed by this line, eg: number of product sold. "
#              "The quantity is not a legal requirement but is very useful for some reports.")
#     price_unit = fields.Float(string='Unit Price', digits='Product Price')
#     discount = fields.Float(string='Discount (%)', digits='Discount', default=0.0)
#     debit = fields.Monetary(string='Debit', default=0.0, currency_field='company_currency_id')
#     credit = fields.Monetary(string='Credit', default=0.0, currency_field='company_currency_id')
#     balance = fields.Monetary(string='Balance', store=True,
#         currency_field='company_currency_id',
#         compute='_compute_balance',
#         help="Technical field holding the debit - credit in order to open meaningful graph views from reports")
#     cumulated_balance = fields.Monetary(string='Cumulated Balance', store=False,
#         currency_field='company_currency_id',
#         compute='_compute_cumulated_balance',
#         help="Cumulated balance depending on the domain and the order chosen in the view.")
#     amount_currency = fields.Monetary(string='Amount in Currency', store=True, copy=True,
#         help="The amount expressed in an optional other currency if it is a multi-currency entry.")
#     price_subtotal = fields.Monetary(string='Subtotal', store=True, readonly=True,
#         currency_field='currency_id')
#     price_total = fields.Monetary(string='Total', store=True, readonly=True,
#         currency_field='currency_id')
#     reconciled = fields.Boolean(compute='_compute_amount_residual', store=True)
#     blocked = fields.Boolean(string='No Follow-up', default=False,
#         help="You can check this box to mark this journal item as a litigation with the associated partner")
#     date_maturity = fields.Date(string='Due Date', index=True, tracking=True,
#         help="This field is used for payable and receivable journal entries. You can put the limit date for the payment of this line.")
#     currency_id = fields.Many2one('res.currency', string='Currency', required=True)
#     partner_id = fields.Many2one('res.partner', string='Partner', ondelete='restrict')
#     product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure', domain="[('category_id', '=', product_uom_category_id)]", ondelete="restrict")
#     product_id = fields.Many2one('product.product', string='Product', ondelete='restrict')
#     product_uom_category_id = fields.Many2one('uom.category', related='product_id.uom_id.category_id')

#     # ==== Origin fields ====
#     reconcile_model_id = fields.Many2one('account.reconcile.model', string="Reconciliation Model", copy=False, readonly=True, check_company=True)
#     payment_id = fields.Many2one('account.payment', index=True, store=True,
#         string="Originator Payment",
#         related='move_id.payment_id',
#         help="The payment that created this entry")
#     statement_line_id = fields.Many2one('account.bank.statement.line', index=True, store=True,
#         string="Originator Statement Line",
#         related='move_id.statement_line_id',
#         help="The statement line that created this entry")
#     statement_id = fields.Many2one(related='statement_line_id.statement_id', store=True, index=True, copy=False,
#         help="The bank statement used for bank reconciliation")

#     # ==== Tax fields ====
#     tax_ids = fields.Many2many(
#         comodel_name='account.tax',
#         string="Taxes",
#         context={'active_test': False},
#         check_company=True,
#         help="Taxes that apply on the base amount")
#     group_tax_id = fields.Many2one(
#         comodel_name='account.tax',
#         string="Originator Group of Taxes",
#         index=True,
#         help="The group of taxes that generated this tax line",
#     )
#     tax_line_id = fields.Many2one('account.tax', string='Originator Tax', ondelete='restrict', store=True,
#         compute='_compute_tax_line_id', help="Indicates that this journal item is a tax line")
#     tax_group_id = fields.Many2one(related='tax_line_id.tax_group_id', string='Originator tax group',
#         readonly=True, store=True,
#         help='technical field for widget tax-group-custom-field')
#     tax_base_amount = fields.Monetary(string="Base Amount", store=True, readonly=True,
#         currency_field='company_currency_id')
#     tax_repartition_line_id = fields.Many2one(comodel_name='account.tax.repartition.line',
#         string="Originator Tax Distribution Line", ondelete='restrict', readonly=True,
#         check_company=True,
#         help="Tax distribution line that caused the creation of this move line, if any")
#     tax_tag_ids = fields.Many2many(string="Tags", comodel_name='account.account.tag', ondelete='restrict',
#         help="Tags assigned to this line by the tax creating it, if any. It determines its impact on financial reports.", tracking=True)
#     tax_audit = fields.Char(string="Tax Audit String", compute="_compute_tax_audit", store=True,
#         help="Computed field, listing the tax grids impacted by this line, and the amount it applies to each of them.")
#     tax_tag_invert = fields.Boolean(string="Invert Tags", compute='_compute_tax_tag_invert', store=True, readonly=False,
#         help="Technical field. True if the balance of this move line needs to be "
#              "inverted when computing its total for each tag (for sales invoices, for example).")

#     # ==== Reconciliation fields ====
#     amount_residual = fields.Monetary(string='Residual Amount', store=True,
#         currency_field='company_currency_id',
#         compute='_compute_amount_residual',
#         help="The residual amount on a journal item expressed in the company currency.")
#     amount_residual_currency = fields.Monetary(string='Residual Amount in Currency', store=True,
#         compute='_compute_amount_residual',
#         help="The residual amount on a journal item expressed in its currency (possibly not the company currency).")
#     full_reconcile_id = fields.Many2one('account.full.reconcile', string="Matching", copy=False, index=True, readonly=True)
#     matched_debit_ids = fields.One2many('account.partial.reconcile', 'credit_move_id', string='Matched Debits',
#         help='Debit journal items that are matched with this journal item.', readonly=True)
#     matched_credit_ids = fields.One2many('account.partial.reconcile', 'debit_move_id', string='Matched Credits',
#         help='Credit journal items that are matched with this journal item.', readonly=True)
#     matching_number = fields.Char(string="Matching #", compute='_compute_matching_number', store=True, help="Matching number for this line, 'P' if it is only partially reconcile, or the name of the full reconcile if it exists.")

#     # ==== Analytic fields ====
#     analytic_line_ids = fields.One2many('account.analytic.line', 'move_id', string='Analytic lines')
#     analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account',
#         index=True, compute="_compute_analytic_account_id", store=True, readonly=False, check_company=True, copy=True)
#     analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags',
#         compute="_compute_analytic_tag_ids", store=True, readonly=False, check_company=True, copy=True)

#     # ==== Onchange / display purpose fields ====
#     recompute_tax_line = fields.Boolean(store=False, readonly=True,
#         help="Technical field used to know on which lines the taxes must be recomputed.")
#     display_type = fields.Selection([
#         ('line_section', 'Section'),
#         ('line_note', 'Note'),
#     ], default=False, help="Technical field for UX purpose.")
#     is_rounding_line = fields.Boolean(help="Technical field used to retrieve the cash rounding line.")
#     exclude_from_invoice_tab = fields.Boolean(help="Technical field used to exclude some lines from the invoice_line_ids tab in the form view.")

#     _sql_constraints = [
#         (
#             'check_credit_debit',
#             'CHECK(credit + debit>=0 AND credit * debit=0)',
#             'Wrong credit or debit value in accounting entry !'
#         ),
#         (
#             'check_accountable_required_fields',
#              "CHECK(COALESCE(display_type IN ('line_section', 'line_note'), 'f') OR account_id IS NOT NULL)",
#              "Missing required account on accountable invoice line."
#         ),
#         (
#             'check_non_accountable_fields_null',
#              "CHECK(display_type NOT IN ('line_section', 'line_note') OR (amount_currency = 0 AND debit = 0 AND credit = 0 AND account_id IS NULL))",
#              "Forbidden unit price, account and quantity on non-accountable invoice line"
#         ),
#         (
#             'check_amount_currency_balance_sign',
#             '''CHECK(
#                 (
#                     (currency_id != company_currency_id)
#                     AND
#                     (
#                         (debit - credit <= 0 AND amount_currency <= 0)
#                         OR
#                         (debit - credit >= 0 AND amount_currency >= 0)
#                     )
#                 )
#                 OR
#                 (
#                     currency_id = company_currency_id
#                     AND
#                     ROUND(debit - credit - amount_currency, 2) = 0
#                 )
#             )''',
#             "The amount expressed in the secondary currency must be positive when account is debited and negative when "
#             "account is credited. If the currency is the same as the one from the company, this amount must strictly "
#             "be equal to the balance."
#         ),
#     ]

#     # -------------------------------------------------------------------------
#     # HELPERS
#     # -------------------------------------------------------------------------

#     @api.model
#     def _get_default_line_name(self, document, amount, currency, date, partner=None):
#         ''' Helper to construct a default label to set on journal items.

#         E.g. Vendor Reimbursement $ 1,555.00 - Azure Interior - 05/14/2020.

#         :param document:    A string representing the type of the document.
#         :param amount:      The document's amount.
#         :param currency:    The document's currency.
#         :param date:        The document's date.
#         :param partner:     The optional partner.
#         :return:            A string.
#         '''
#         values = ['%s %s' % (document, formatLang(self.env, amount, currency_obj=currency))]
#         if partner:
#             values.append(partner.display_name)
#         values.append(format_date(self.env, fields.Date.to_string(date)))
#         return ' - '.join(values)

#     @api.model
#     def _get_default_tax_account(self, repartition_line):
#         tax = repartition_line.invoice_tax_id or repartition_line.refund_tax_id
#         if tax.tax_exigibility == 'on_payment':
#             account = tax.cash_basis_transition_account_id
#         else:
#             account = repartition_line.account_id
#         return account

#     def _get_computed_name(self):
#         self.ensure_one()

#         if not self.product_id:
#             return ''

#         if self.partner_id.lang:
#             product = self.product_id.with_context(lang=self.partner_id.lang)
#         else:
#             product = self.product_id

#         values = []
#         if product.partner_ref:
#             values.append(product.partner_ref)
#         if self.journal_id.type == 'sale':
#             if product.description_sale:
#                 values.append(product.description_sale)
#         elif self.journal_id.type == 'purchase':
#             if product.description_purchase:
#                 values.append(product.description_purchase)
#         return '\n'.join(values)

#     def _get_computed_price_unit(self):
#         ''' Helper to get the default price unit based on the product by taking care of the taxes
#         set on the product and the fiscal position.
#         :return: The price unit.
#         '''
#         self.ensure_one()

#         if not self.product_id:
#             return 0.0
#         if self.move_id.is_sale_document(include_receipts=True):
#             document_type = 'sale'
#         elif self.move_id.is_purchase_document(include_receipts=True):
#             document_type = 'purchase'
#         else:
#             document_type = 'other'

#         return self.product_id._get_tax_included_unit_price(
#             self.move_id.company_id,
#             self.move_id.currency_id,
#             self.move_id.date,
#             document_type,
#             fiscal_position=self.move_id.fiscal_position_id,
#             product_uom=self.product_uom_id
#         )

#     def _get_computed_account(self):
#         self.ensure_one()
#         self = self.with_company(self.move_id.journal_id.company_id)

#         if not self.product_id:
#             return

#         fiscal_position = self.move_id.fiscal_position_id
#         accounts = self.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=fiscal_position)
#         if self.move_id.is_sale_document(include_receipts=True):
#             # Out invoice.
#             return accounts['income'] or self.account_id
#         elif self.move_id.is_purchase_document(include_receipts=True):
#             # In invoice.
#             return accounts['expense'] or self.account_id

#     def _get_computed_taxes(self):
#         self.ensure_one()

#         if self.move_id.is_sale_document(include_receipts=True):
#             # Out invoice.
#             if self.product_id.taxes_id:
#                 tax_ids = self.product_id.taxes_id.filtered(lambda tax: tax.company_id == self.move_id.company_id)
#             elif self.account_id.tax_ids:
#                 tax_ids = self.account_id.tax_ids
#             else:
#                 tax_ids = self.env['account.tax']
#             if not tax_ids and not self.exclude_from_invoice_tab:
#                 tax_ids = self.move_id.company_id.account_sale_tax_id
#         elif self.move_id.is_purchase_document(include_receipts=True):
#             # In invoice.
#             if self.product_id.supplier_taxes_id:
#                 tax_ids = self.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == self.move_id.company_id)
#             elif self.account_id.tax_ids:
#                 tax_ids = self.account_id.tax_ids
#             else:
#                 tax_ids = self.env['account.tax']
#             if not tax_ids and not self.exclude_from_invoice_tab:
#                 tax_ids = self.move_id.company_id.account_purchase_tax_id
#         else:
#             # Miscellaneous operation.
#             tax_ids = self.account_id.tax_ids

#         if self.company_id and tax_ids:
#             tax_ids = tax_ids.filtered(lambda tax: tax.company_id == self.company_id)

#         return tax_ids

#     def _get_computed_uom(self):
#         self.ensure_one()
#         if self.product_id:
#             return self.product_id.uom_id
#         return False

#     def _set_price_and_tax_after_fpos(self):
#         self.ensure_one()
#         # Manage the fiscal position after that and adapt the price_unit.
#         # E.g. mapping a price-included-tax to a price-excluded-tax must
#         # remove the tax amount from the price_unit.
#         # However, mapping a price-included tax to another price-included tax must preserve the balance but
#         # adapt the price_unit to the new tax.
#         # E.g. mapping a 10% price-included tax to a 20% price-included tax for a price_unit of 110 should preserve
#         # 100 as balance but set 120 as price_unit.
#         if self.tax_ids and self.move_id.fiscal_position_id and self.move_id.fiscal_position_id.tax_ids:
#             price_subtotal = self._get_price_total_and_subtotal()['price_subtotal']
#             self.tax_ids = self.move_id.fiscal_position_id.map_tax(self.tax_ids._origin)
#             accounting_vals = self._get_fields_onchange_subtotal(
#                 price_subtotal=price_subtotal,
#                 currency=self.move_id.company_currency_id)
#             amount_currency = accounting_vals['amount_currency']
#             business_vals = self._get_fields_onchange_balance(amount_currency=amount_currency)
#             if 'price_unit' in business_vals:
#                 self.price_unit = business_vals['price_unit']

#     @api.depends('product_id', 'account_id', 'partner_id', 'date')
#     def _compute_analytic_account_id(self):
#         for record in self:
#             if not record.exclude_from_invoice_tab or not record.move_id.is_invoice(include_receipts=True):
#                 rec = self.env['account.analytic.default'].account_get(
#                     product_id=record.product_id.id,
#                     partner_id=record.partner_id.commercial_partner_id.id or record.move_id.partner_id.commercial_partner_id.id,
#                     account_id=record.account_id.id,
#                     user_id=record.env.uid,
#                     date=record.date,
#                     company_id=record.move_id.company_id.id
#                 )
#                 if rec:
#                     record.analytic_account_id = rec.analytic_id

#     @api.depends('product_id', 'account_id', 'partner_id', 'date')
#     def _compute_analytic_tag_ids(self):
#         for record in self:
#             if not record.exclude_from_invoice_tab or not record.move_id.is_invoice(include_receipts=True):
#                 rec = self.env['account.analytic.default'].account_get(
#                     product_id=record.product_id.id,
#                     partner_id=record.partner_id.commercial_partner_id.id or record.move_id.partner_id.commercial_partner_id.id,
#                     account_id=record.account_id.id,
#                     user_id=record.env.uid,
#                     date=record.date,
#                     company_id=record.move_id.company_id.id
#                 )
#                 if rec:
#                     record.analytic_tag_ids = rec.analytic_tag_ids

#     def _get_price_total_and_subtotal(self, price_unit=None, quantity=None, discount=None, currency=None, product=None, partner=None, taxes=None, move_type=None):
#         self.ensure_one()
#         return self._get_price_total_and_subtotal_model(
#             price_unit=price_unit or self.price_unit,
#             quantity=quantity or self.quantity,
#             discount=discount or self.discount,
#             currency=currency or self.currency_id,
#             product=product or self.product_id,
#             partner=partner or self.partner_id,
#             taxes=taxes or self.tax_ids,
#             move_type=move_type or self.move_id.move_type,
#         )

#     @api.model
#     def _get_price_total_and_subtotal_model(self, price_unit, quantity, discount, currency, product, partner, taxes, move_type):
#         ''' This method is used to compute 'price_total' & 'price_subtotal'.

#         :param price_unit:  The current price unit.
#         :param quantity:    The current quantity.
#         :param discount:    The current discount.
#         :param currency:    The line's currency.
#         :param product:     The line's product.
#         :param partner:     The line's partner.
#         :param taxes:       The applied taxes.
#         :param move_type:   The type of the move.
#         :return:            A dictionary containing 'price_subtotal' & 'price_total'.
#         '''
#         res = {}

#         # Compute 'price_subtotal'.
#         line_discount_price_unit = price_unit * (1 - (discount / 100.0))
#         subtotal = quantity * line_discount_price_unit

#         # Compute 'price_total'.
#         if taxes:
#             taxes_res = taxes._origin.with_context(force_sign=1).compute_all(line_discount_price_unit,
#                 quantity=quantity, currency=currency, product=product, partner=partner, is_refund=move_type in ('out_refund', 'in_refund'))
#             res['price_subtotal'] = taxes_res['total_excluded']
#             res['price_total'] = taxes_res['total_included']
#         else:
#             res['price_total'] = res['price_subtotal'] = subtotal
#         #In case of multi currency, round before it's use for computing debit credit
#         if currency:
#             res = {k: currency.round(v) for k, v in res.items()}
#         return res

#     def _get_fields_onchange_subtotal(self, price_subtotal=None, move_type=None, currency=None, company=None, date=None):
#         self.ensure_one()
#         return self._get_fields_onchange_subtotal_model(
#             price_subtotal=price_subtotal or self.price_subtotal,
#             move_type=move_type or self.move_id.move_type,
#             currency=currency or self.currency_id,
#             company=company or self.move_id.company_id,
#             date=date or self.move_id.date,
#         )

#     @api.model
#     def _get_fields_onchange_subtotal_model(self, price_subtotal, move_type, currency, company, date):
#         ''' This method is used to recompute the values of 'amount_currency', 'debit', 'credit' due to a change made
#         in some business fields (affecting the 'price_subtotal' field).

#         :param price_subtotal:  The untaxed amount.
#         :param move_type:       The type of the move.
#         :param currency:        The line's currency.
#         :param company:         The move's company.
#         :param date:            The move's date.
#         :return:                A dictionary containing 'debit', 'credit', 'amount_currency'.
#         '''
#         if move_type in self.move_id.get_outbound_types():
#             sign = 1
#         elif move_type in self.move_id.get_inbound_types():
#             sign = -1
#         else:
#             sign = 1

#         amount_currency = price_subtotal * sign
#         balance = currency._convert(amount_currency, company.currency_id, company, date or fields.Date.context_today(self))
#         return {
#             'amount_currency': amount_currency,
#             'currency_id': currency.id,
#             'debit': balance > 0.0 and balance or 0.0,
#             'credit': balance < 0.0 and -balance or 0.0,
#         }

#     def _get_fields_onchange_balance(self, quantity=None, discount=None, amount_currency=None, move_type=None, currency=None, taxes=None, price_subtotal=None, force_computation=False):
#         self.ensure_one()
#         return self._get_fields_onchange_balance_model(
#             quantity=quantity or self.quantity,
#             discount=discount or self.discount,
#             amount_currency=amount_currency or self.amount_currency,
#             move_type=move_type or self.move_id.move_type,
#             currency=currency or self.currency_id or self.move_id.currency_id,
#             taxes=taxes or self.tax_ids,
#             price_subtotal=price_subtotal or self.price_subtotal,
#             force_computation=force_computation,
#         )

#     @api.model
#     def _get_fields_onchange_balance_model(self, quantity, discount, amount_currency, move_type, currency, taxes, price_subtotal, force_computation=False):
#         ''' This method is used to recompute the values of 'quantity', 'discount', 'price_unit' due to a change made
#         in some accounting fields such as 'balance'.

#         This method is a bit complex as we need to handle some special cases.
#         For example, setting a positive balance with a 100% discount.

#         :param quantity:        The current quantity.
#         :param discount:        The current discount.
#         :param amount_currency: The new balance in line's currency.
#         :param move_type:       The type of the move.
#         :param currency:        The currency.
#         :param taxes:           The applied taxes.
#         :param price_subtotal:  The price_subtotal.
#         :return:                A dictionary containing 'quantity', 'discount', 'price_unit'.
#         '''
#         if move_type in self.move_id.get_outbound_types():
#             sign = 1
#         elif move_type in self.move_id.get_inbound_types():
#             sign = -1
#         else:
#             sign = 1
#         amount_currency *= sign

#         # Avoid rounding issue when dealing with price included taxes. For example, when the price_unit is 2300.0 and
#         # a 5.5% price included tax is applied on it, a balance of 2300.0 / 1.055 = 2180.094 ~ 2180.09 is computed.
#         # However, when triggering the inverse, 2180.09 + (2180.09 * 0.055) = 2180.09 + 119.90 = 2299.99 is computed.
#         # To avoid that, set the price_subtotal at the balance if the difference between them looks like a rounding
#         # issue.
#         if not force_computation and currency.is_zero(amount_currency - price_subtotal):
#             return {}

#         taxes = taxes.flatten_taxes_hierarchy()
#         if taxes and any(tax.price_include for tax in taxes):
#             # Inverse taxes. E.g:
#             #
#             # Price Unit    | Taxes         | Originator Tax    |Price Subtotal     | Price Total
#             # -----------------------------------------------------------------------------------
#             # 110           | 10% incl, 5%  |                   | 100               | 115
#             # 10            |               | 10% incl          | 10                | 10
#             # 5             |               | 5%                | 5                 | 5
#             #
#             # When setting the balance to -200, the expected result is:
#             #
#             # Price Unit    | Taxes         | Originator Tax    |Price Subtotal     | Price Total
#             # -----------------------------------------------------------------------------------
#             # 220           | 10% incl, 5%  |                   | 200               | 230
#             # 20            |               | 10% incl          | 20                | 20
#             # 10            |               | 5%                | 10                | 10
#             force_sign = -1 if move_type in ('out_invoice', 'in_refund', 'out_receipt') else 1
#             taxes_res = taxes._origin.with_context(force_sign=force_sign).compute_all(amount_currency, currency=currency, handle_price_include=False)
#             for tax_res in taxes_res['taxes']:
#                 tax = self.env['account.tax'].browse(tax_res['id'])
#                 if tax.price_include:
#                     amount_currency += tax_res['amount']

#         discount_factor = 1 - (discount / 100.0)
#         if amount_currency and discount_factor:
#             # discount != 100%
#             vals = {
#                 'quantity': quantity or 1.0,
#                 'price_unit': amount_currency / discount_factor / (quantity or 1.0),
#             }
#         elif amount_currency and not discount_factor:
#             # discount == 100%
#             vals = {
#                 'quantity': quantity or 1.0,
#                 'discount': 0.0,
#                 'price_unit': amount_currency / (quantity or 1.0),
#             }
#         elif not discount_factor:
#             # balance of line is 0, but discount  == 100% so we display the normal unit_price
#             vals = {}
#         else:
#             # balance is 0, so unit price is 0 as well
#             vals = {'price_unit': 0.0}
#         return vals

#     @api.model
#     def _get_tax_exigible_domain(self):
#         """ Returns a domain to be used to identify the move lines that are allowed
#         to be taken into account in the tax report.
#         """
#         return [
#             # Lines on moves without any payable or receivable line are always exigible
#             '|', ('move_id.always_tax_exigible', '=', True),

#             # Lines with only tags are always exigible
#             '|', '&', ('tax_line_id', '=', False), ('tax_ids', '=', False),

#             # Lines from CABA entries are always exigible
#             '|', ('move_id.tax_cash_basis_rec_id', '!=', False),

#             # Lines from non-CABA taxes are always exigible
#             '|', ('tax_line_id.tax_exigibility', '!=', 'on_payment'),
#             ('tax_ids.tax_exigibility', '!=', 'on_payment'), # So: exigible if at least one tax from tax_ids isn't on_payment
#         ]

#     def belongs_to_refund(self):
#         """ Tells whether or not this move line corresponds to a refund operation.
#         """
#         self.ensure_one()

#         if self.tax_repartition_line_id:
#             return self.tax_repartition_line_id.refund_tax_id

#         elif self.move_id.move_type == 'entry':
#             tax_type = self.tax_ids[0].type_tax_use if self.tax_ids else None
#             return (tax_type == 'sale' and self.debit) or (tax_type == 'purchase' and self.credit)

#         return self.move_id.move_type in ('in_refund', 'out_refund')

#     def _get_invoiced_qty_per_product(self):
#         qties = defaultdict(float)
#         for aml in self:
#             qty = aml.product_uom_id._compute_quantity(aml.quantity, aml.product_id.uom_id)
#             if aml.move_id.move_type == 'out_invoice':
#                 qties[aml.product_id] += qty
#             elif aml.move_id.move_type == 'out_refund':
#                 qties[aml.product_id] -= qty
#         return qties

#     # -------------------------------------------------------------------------
#     # ONCHANGE METHODS
#     # -------------------------------------------------------------------------

#     @api.onchange('amount_currency', 'currency_id', 'debit', 'credit', 'tax_ids', 'account_id', 'price_unit', 'quantity')
#     def _onchange_mark_recompute_taxes(self):
#         ''' Recompute the dynamic onchange based on taxes.
#         If the edited line is a tax line, don't recompute anything as the user must be able to
#         set a custom value.
#         '''
#         for line in self:
#             if not line.tax_repartition_line_id:
#                 line.recompute_tax_line = True

#     @api.onchange('analytic_account_id', 'analytic_tag_ids')
#     def _onchange_mark_recompute_taxes_analytic(self):
#         ''' Trigger tax recomputation only when some taxes with analytics
#         '''
#         for line in self:
#             if not line.tax_repartition_line_id and any(tax.analytic for tax in line.tax_ids):
#                 line.recompute_tax_line = True

#     @api.onchange('product_id')
#     def _onchange_product_id(self):
#         for line in self:
#             if not line.product_id or line.display_type in ('line_section', 'line_note'):
#                 continue

#             line.name = line._get_computed_name()
#             line.account_id = line._get_computed_account()
#             taxes = line._get_computed_taxes()
#             if taxes and line.move_id.fiscal_position_id:
#                 taxes = line.move_id.fiscal_position_id.map_tax(taxes)
#             line.tax_ids = taxes
#             line.product_uom_id = line._get_computed_uom()
#             line.price_unit = line._get_computed_price_unit()

#     @api.onchange('product_uom_id')
#     def _onchange_uom_id(self):
#         ''' Recompute the 'price_unit' depending of the unit of measure. '''
#         if self.display_type in ('line_section', 'line_note'):
#             return
#         taxes = self._get_computed_taxes()
#         if taxes and self.move_id.fiscal_position_id:
#             taxes = self.move_id.fiscal_position_id.map_tax(taxes)
#         self.tax_ids = taxes
#         self.price_unit = self._get_computed_price_unit()

#     @api.onchange('account_id')
#     def _onchange_account_id(self):
#         ''' Recompute 'tax_ids' based on 'account_id'.
#         /!\ Don't remove existing taxes if there is no explicit taxes set on the account.
#         '''
#         for line in self:
#             if not line.display_type and (line.account_id.tax_ids or not line.tax_ids):
#                 taxes = line._get_computed_taxes()

#                 if taxes and line.move_id.fiscal_position_id:
#                     taxes = line.move_id.fiscal_position_id.map_tax(taxes)

#                 line.tax_ids = taxes

#     def _onchange_balance(self):
#         for line in self:
#             if line.currency_id == line.move_id.company_id.currency_id:
#                 line.amount_currency = line.balance
#             else:
#                 continue
#             if not line.move_id.is_invoice(include_receipts=True):
#                 continue
#             line.update(line._get_fields_onchange_balance())

#     @api.onchange('debit')
#     def _onchange_debit(self):
#         if self.debit:
#             self.credit = 0.0
#         self._onchange_balance()

#     @api.onchange('credit')
#     def _onchange_credit(self):
#         if self.credit:
#             self.debit = 0.0
#         self._onchange_balance()

#     @api.onchange('amount_currency')
#     def _onchange_amount_currency(self):
#         for line in self:
#             company = line.move_id.company_id
#             balance = line.currency_id._convert(line.amount_currency, company.currency_id, company, line.move_id.date or fields.Date.context_today(line))
#             line.debit = balance if balance > 0.0 else 0.0
#             line.credit = -balance if balance < 0.0 else 0.0

#             if not line.move_id.is_invoice(include_receipts=True):
#                 continue

#             line.update(line._get_fields_onchange_balance())
#             line.update(line._get_price_total_and_subtotal())

#     @api.onchange('quantity', 'discount', 'price_unit', 'tax_ids')
#     def _onchange_price_subtotal(self):
#         for line in self:
#             if not line.move_id.is_invoice(include_receipts=True):
#                 continue

#             line.update(line._get_price_total_and_subtotal())
#             line.update(line._get_fields_onchange_subtotal())

#     @api.onchange('currency_id')
#     def _onchange_currency(self):
#         for line in self:
#             company = line.move_id.company_id

#             if line.move_id.is_invoice(include_receipts=True):
#                 line._onchange_price_subtotal()
#             elif not line.move_id.reversed_entry_id:
#                 balance = line.currency_id._convert(line.amount_currency, company.currency_id, company, line.move_id.date or fields.Date.context_today(line))
#                 line.debit = balance if balance > 0.0 else 0.0
#                 line.credit = -balance if balance < 0.0 else 0.0

#     # -------------------------------------------------------------------------
#     # COMPUTE METHODS
#     # -------------------------------------------------------------------------

#     @api.depends('full_reconcile_id.name', 'matched_debit_ids', 'matched_credit_ids')
#     def _compute_matching_number(self):
#         for record in self:
#             if record.full_reconcile_id:
#                 record.matching_number = record.full_reconcile_id.name
#             elif record.matched_debit_ids or record.matched_credit_ids:
#                 record.matching_number = 'P'
#             else:
#                 record.matching_number = None

#     @api.depends('debit', 'credit')
#     def _compute_balance(self):
#         for line in self:
#             line.balance = line.debit - line.credit

#     @api.model
#     def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
#         def to_tuple(t):
#             return tuple(map(to_tuple, t)) if isinstance(t, (list, tuple)) else t
#         # Make an explicit order because we will need to reverse it
#         order = (order or self._order) + ', id'
#         # Add the domain and order by in order to compute the cumulated balance in _compute_cumulated_balance
#         return super(AccountMoveLine, self.with_context(domain_cumulated_balance=to_tuple(domain or []), order_cumulated_balance=order)).search_read(domain, fields, offset, limit, order)

#     @api.depends_context('order_cumulated_balance', 'domain_cumulated_balance')
#     def _compute_cumulated_balance(self):
#         if not self.env.context.get('order_cumulated_balance'):
#             # We do not come from search_read, so we are not in a list view, so it doesn't make any sense to compute the cumulated balance
#             self.cumulated_balance = 0
#             return

#         # get the where clause
#         query = self._where_calc(list(self.env.context.get('domain_cumulated_balance') or []))
#         order_string = ", ".join(self._generate_order_by_inner(self._table, self.env.context.get('order_cumulated_balance'), query, reverse_direction=True))
#         from_clause, where_clause, where_clause_params = query.get_sql()
#         sql = """
#             SELECT account_move_line.id, SUM(account_move_line.balance) OVER (
#                 ORDER BY %(order_by)s
#                 ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
#             )
#             FROM %(from)s
#             WHERE %(where)s
#         """ % {'from': from_clause, 'where': where_clause or 'TRUE', 'order_by': order_string}
#         self.env.cr.execute(sql, where_clause_params)
#         result = {r[0]: r[1] for r in self.env.cr.fetchall()}
#         for record in self:
#             record.cumulated_balance = result[record.id]

#     @api.depends('debit', 'credit', 'amount_currency', 'account_id', 'currency_id', 'move_id.state', 'company_id',
#                  'matched_debit_ids', 'matched_credit_ids')
#     def _compute_amount_residual(self):
#         """ Computes the residual amount of a move line from a reconcilable account in the company currency and the line's currency.
#             This amount will be 0 for fully reconciled lines or lines from a non-reconcilable account, the original line amount
#             for unreconciled lines, and something in-between for partially reconciled lines.
#         """
#         for line in self:
#             if line.id and (line.account_id.reconcile or line.account_id.internal_type == 'liquidity'):
#                 reconciled_balance = sum(line.matched_credit_ids.mapped('amount')) \
#                                      - sum(line.matched_debit_ids.mapped('amount'))
#                 reconciled_amount_currency = sum(line.matched_credit_ids.mapped('debit_amount_currency'))\
#                                              - sum(line.matched_debit_ids.mapped('credit_amount_currency'))

#                 line.amount_residual = line.balance - reconciled_balance

#                 if line.currency_id:
#                     line.amount_residual_currency = line.amount_currency - reconciled_amount_currency
#                 else:
#                     line.amount_residual_currency = 0.0

#                 line.reconciled = line.company_currency_id.is_zero(line.amount_residual) \
#                                   and (not line.currency_id or line.currency_id.is_zero(line.amount_residual_currency))
#             else:
#                 # Must not have any reconciliation since the line is not eligible for that.
#                 line.amount_residual = 0.0
#                 line.amount_residual_currency = 0.0
#                 line.reconciled = False

#     @api.depends('tax_repartition_line_id.invoice_tax_id', 'tax_repartition_line_id.refund_tax_id')
#     def _compute_tax_line_id(self):
#         """ tax_line_id is computed as the tax linked to the repartition line creating
#         the move.
#         """
#         for record in self:
#             rep_line = record.tax_repartition_line_id
#             # A constraint on account.tax.repartition.line ensures both those fields are mutually exclusive
#             record.tax_line_id = rep_line.invoice_tax_id or rep_line.refund_tax_id

#     @api.depends('move_id.move_type', 'tax_ids', 'tax_repartition_line_id', 'debit', 'credit', 'tax_tag_ids')
#     def _compute_tax_tag_invert(self):
#         for record in self:
#             if not record.tax_repartition_line_id and not record.tax_ids :
#                 # Invoices imported from other softwares might only have kept the tags, not the taxes.
#                 record.tax_tag_invert = record.tax_tag_ids and record.move_id.is_inbound()

#             elif record.move_id.move_type == 'entry':
#                 # For misc operations, cash basis entries and write-offs from the bank reconciliation widget
#                 rep_line = record.tax_repartition_line_id
#                 if rep_line:
#                     tax_type = (rep_line.refund_tax_id or rep_line.invoice_tax_id).type_tax_use
#                     is_refund = bool(rep_line.refund_tax_id)
#                 elif record.tax_ids:
#                     tax_type = record.tax_ids[0].type_tax_use
#                     is_refund = (tax_type == 'sale' and record.debit) or (tax_type == 'purchase' and record.credit)

#                 record.tax_tag_invert = (tax_type == 'purchase' and is_refund) or (tax_type == 'sale' and not is_refund)

#             else:
#                 # For invoices with taxes
#                 record.tax_tag_invert = record.move_id.is_inbound()

#     @api.depends('tax_tag_ids', 'debit', 'credit', 'journal_id', 'tax_tag_invert')
#     def _compute_tax_audit(self):
#         separator = '        '

#         for record in self:
#             currency = record.company_id.currency_id
#             audit_str = ''
#             for tag in record.tax_tag_ids:
#                 tag_amount = (record.tax_tag_invert and -1 or 1) * (tag.tax_negate and -1 or 1) * record.balance

#                 if tag.tax_report_line_ids:
#                     #Then, the tag comes from a report line, and hence has a + or - sign (also in its name)
#                     for report_line in tag.tax_report_line_ids:
#                         audit_str += separator if audit_str else ''
#                         audit_str += report_line.tag_name + ': ' + formatLang(self.env, tag_amount, currency_obj=currency)
#                 else:
#                     # Then, it's a financial tag (sign is always +, and never shown in tag name)
#                     audit_str += separator if audit_str else ''
#                     audit_str += tag.name + ': ' + formatLang(self.env, tag_amount, currency_obj=currency)

#             record.tax_audit = audit_str

#     # -------------------------------------------------------------------------
#     # CONSTRAINT METHODS
#     # -------------------------------------------------------------------------

#     @api.constrains('account_id', 'journal_id')
#     def _check_constrains_account_id_journal_id(self):
#         for line in self.filtered(lambda x: x.display_type not in ('line_section', 'line_note')):
#             account = line.account_id
#             journal = line.move_id.journal_id

#             if account.deprecated:
#                 raise UserError(_('The account %s (%s) is deprecated.') % (account.name, account.code))

#             account_currency = account.currency_id
#             if account_currency and account_currency != line.company_currency_id and account_currency != line.currency_id:
#                 raise UserError(_('The account selected on your journal entry forces to provide a secondary currency. You should remove the secondary currency on the account.'))

#             if account.allowed_journal_ids and journal not in account.allowed_journal_ids:
#                 raise UserError(_('You cannot use this account (%s) in this journal, check the field \'Allowed Journals\' on the related account.', account.display_name))

#             failed_check = False
#             if (journal.type_control_ids - journal.default_account_id.user_type_id) or journal.account_control_ids:
#                 failed_check = True
#                 if journal.type_control_ids:
#                     failed_check = account.user_type_id not in (journal.type_control_ids - journal.default_account_id.user_type_id)
#                 if failed_check and journal.account_control_ids:
#                     failed_check = account not in journal.account_control_ids

#             if failed_check:
#                 raise UserError(_('You cannot use this account (%s) in this journal, check the section \'Control-Access\' under tab \'Advanced Settings\' on the related journal.', account.display_name))

#     @api.constrains('account_id', 'tax_ids', 'tax_line_id', 'reconciled')
#     def _check_off_balance(self):
#         for line in self:
#             if line.account_id.internal_group == 'off_balance':
#                 if any(a.internal_group != line.account_id.internal_group for a in line.move_id.line_ids.account_id):
#                     raise UserError(_('If you want to use "Off-Balance Sheet" accounts, all the accounts of the journal entry must be of this type'))
#                 if line.tax_ids or line.tax_line_id:
#                     raise UserError(_('You cannot use taxes on lines with an Off-Balance account'))
#                 if line.reconciled:
#                     raise UserError(_('Lines from "Off-Balance Sheet" accounts cannot be reconciled'))

#     def _affect_tax_report(self):
#         self.ensure_one()
#         return self.tax_ids or self.tax_line_id or self.tax_tag_ids.filtered(lambda x: x.applicability == "taxes")

#     def _check_tax_lock_date(self):
#         for line in self.filtered(lambda l: l.move_id.state == 'posted'):
#             move = line.move_id
#             if move.company_id.tax_lock_date and move.date <= move.company_id.tax_lock_date and line._affect_tax_report():
#                 raise UserError(_("The operation is refused as it would impact an already issued tax statement. "
#                                   "Please change the journal entry date or the tax lock date set in the settings (%s) to proceed.")
#                                 % format_date(self.env, move.company_id.tax_lock_date))

#     def _check_reconciliation(self):
#         for line in self:
#             if line.matched_debit_ids or line.matched_credit_ids:
#                 raise UserError(_("You cannot do this modification on a reconciled journal entry. "
#                                   "You can just change some non legal fields or you must unreconcile first.\n"
#                                   "Journal Entry (id): %s (%s)") % (line.move_id.name, line.move_id.id))

#     @api.constrains('tax_ids', 'tax_repartition_line_id')
#     def _check_caba_non_caba_shared_tags(self):
#         """ When mixing cash basis and non cash basis taxes, it is important
#         that those taxes don't share tags on the repartition creating
#         a single account.move.line.

#         Shared tags in this context cannot work, as the tags would need to
#         be present on both the invoice and cash basis move, leading to the same
#         base amount to be taken into account twice; which is wrong.This is
#         why we don't support that. A workaround may be provided by the use of
#         a group of taxes, whose children are type_tax_use=None, and only one
#         of them uses the common tag.

#         Note that taxes of the same exigibility are allowed to share tags.
#         """
#         def get_base_repartition(base_aml, taxes):
#             if not taxes:
#                 return self.env['account.tax.repartition.line']

#             is_refund = base_aml.belongs_to_refund()
#             repartition_field = is_refund and 'refund_repartition_line_ids' or 'invoice_repartition_line_ids'
#             return taxes.mapped(repartition_field)

#         for aml in self:
#             caba_taxes = aml.tax_ids.filtered(lambda x: x.tax_exigibility == 'on_payment')
#             non_caba_taxes = aml.tax_ids - caba_taxes

#             caba_base_tags = get_base_repartition(aml, caba_taxes).filtered(lambda x: x.repartition_type == 'base').tag_ids
#             non_caba_base_tags = get_base_repartition(aml, non_caba_taxes).filtered(lambda x: x.repartition_type == 'base').tag_ids

#             common_tags = caba_base_tags & non_caba_base_tags

#             if not common_tags:
#                 # When a tax is affecting another one with different tax exigibility, tags cannot be shared either.
#                 tax_tags = aml.tax_repartition_line_id.tag_ids
#                 comparison_tags = non_caba_base_tags if aml.tax_repartition_line_id.tax_id.tax_exigibility == 'on_payment' else caba_base_tags
#                 common_tags = tax_tags & comparison_tags

#             if common_tags:
#                 raise ValidationError(_("Taxes exigible on payment and on invoice cannot be mixed on the same journal item if they share some tag."))

#     # -------------------------------------------------------------------------
#     # LOW-LEVEL METHODS
#     # -------------------------------------------------------------------------

#     def init(self):
#         """ change index on partner_id to a multi-column index on (partner_id, ref), the new index will behave in the
#             same way when we search on partner_id, with the addition of being optimal when having a query that will
#             search on partner_id and ref at the same time (which is the case when we open the bank reconciliation widget)
#         """
#         cr = self._cr
#         cr.execute('DROP INDEX IF EXISTS account_move_line_partner_id_index')
#         cr.execute('SELECT indexname FROM pg_indexes WHERE indexname = %s', ('account_move_line_partner_id_ref_idx',))
#         if not cr.fetchone():
#             cr.execute('CREATE INDEX account_move_line_partner_id_ref_idx ON account_move_line (partner_id, ref)')

#     @api.model_create_multi
#     def create(self, vals_list):
#         # OVERRIDE
#         ACCOUNTING_FIELDS = ('debit', 'credit', 'amount_currency')
#         BUSINESS_FIELDS = ('price_unit', 'quantity', 'discount', 'tax_ids')

#         for vals in vals_list:
#             move = self.env['account.move'].browse(vals['move_id'])
#             vals.setdefault('company_currency_id', move.company_id.currency_id.id) # important to bypass the ORM limitation where monetary fields are not rounded; more info in the commit message

#             # Ensure balance == amount_currency in case of missing currency or same currency as the one from the
#             # company.
#             currency_id = vals.get('currency_id') or move.company_id.currency_id.id
#             if currency_id == move.company_id.currency_id.id:
#                 balance = vals.get('debit', 0.0) - vals.get('credit', 0.0)
#                 vals.update({
#                     'currency_id': currency_id,
#                     'amount_currency': balance,
#                 })
#             else:
#                 vals['amount_currency'] = vals.get('amount_currency', 0.0)

#             if move.is_invoice(include_receipts=True):
#                 currency = move.currency_id
#                 partner = self.env['res.partner'].browse(vals.get('partner_id'))
#                 taxes = self.new({'tax_ids': vals.get('tax_ids', [])}).tax_ids
#                 tax_ids = set(taxes.ids)
#                 taxes = self.env['account.tax'].browse(tax_ids)

#                 # Ensure consistency between accounting & business fields.
#                 # As we can't express such synchronization as computed fields without cycling, we need to do it both
#                 # in onchange and in create/write. So, if something changed in accounting [resp. business] fields,
#                 # business [resp. accounting] fields are recomputed.
#                 if any(vals.get(field) for field in ACCOUNTING_FIELDS):
#                     price_subtotal = self._get_price_total_and_subtotal_model(
#                         vals.get('price_unit', 0.0),
#                         vals.get('quantity', 0.0),
#                         vals.get('discount', 0.0),
#                         currency,
#                         self.env['product.product'].browse(vals.get('product_id')),
#                         partner,
#                         taxes,
#                         move.move_type,
#                     ).get('price_subtotal', 0.0)
#                     vals.update(self._get_fields_onchange_balance_model(
#                         vals.get('quantity', 0.0),
#                         vals.get('discount', 0.0),
#                         vals['amount_currency'],
#                         move.move_type,
#                         currency,
#                         taxes,
#                         price_subtotal
#                     ))
#                     vals.update(self._get_price_total_and_subtotal_model(
#                         vals.get('price_unit', 0.0),
#                         vals.get('quantity', 0.0),
#                         vals.get('discount', 0.0),
#                         currency,
#                         self.env['product.product'].browse(vals.get('product_id')),
#                         partner,
#                         taxes,
#                         move.move_type,
#                     ))
#                 elif any(vals.get(field) for field in BUSINESS_FIELDS):
#                     vals.update(self._get_price_total_and_subtotal_model(
#                         vals.get('price_unit', 0.0),
#                         vals.get('quantity', 0.0),
#                         vals.get('discount', 0.0),
#                         currency,
#                         self.env['product.product'].browse(vals.get('product_id')),
#                         partner,
#                         taxes,
#                         move.move_type,
#                     ))
#                     vals.update(self._get_fields_onchange_subtotal_model(
#                         vals['price_subtotal'],
#                         move.move_type,
#                         currency,
#                         move.company_id,
#                         move.date,
#                     ))

#         lines = super(AccountMoveLine, self).create(vals_list)

#         moves = lines.mapped('move_id')
#         if self._context.get('check_move_validity', True):
#             moves._check_balanced()
#         moves.filtered(lambda m: m.state == 'posted')._check_fiscalyear_lock_date()
#         lines.filtered(lambda l: l.parent_state == 'posted')._check_tax_lock_date()
#         moves._synchronize_business_models({'line_ids'})

#         return lines

#     def write(self, vals):
#         # OVERRIDE
#         ACCOUNTING_FIELDS = ('debit', 'credit', 'amount_currency')
#         BUSINESS_FIELDS = ('price_unit', 'quantity', 'discount', 'tax_ids')
#         PROTECTED_FIELDS_TAX_LOCK_DATE = ['debit', 'credit', 'tax_line_id', 'tax_ids', 'tax_tag_ids']
#         PROTECTED_FIELDS_LOCK_DATE = PROTECTED_FIELDS_TAX_LOCK_DATE + ['account_id', 'journal_id', 'amount_currency', 'currency_id', 'partner_id']
#         PROTECTED_FIELDS_RECONCILIATION = ('account_id', 'date', 'debit', 'credit', 'amount_currency', 'currency_id')

#         account_to_write = self.env['account.account'].browse(vals['account_id']) if 'account_id' in vals else None

#         # Check writing a deprecated account.
#         if account_to_write and account_to_write.deprecated:
#             raise UserError(_('You cannot use a deprecated account.'))

#         for line in self:
#             if line.parent_state == 'posted':
#                 if line.move_id.restrict_mode_hash_table and set(vals).intersection(INTEGRITY_HASH_LINE_FIELDS):
#                     raise UserError(_("You cannot edit the following fields due to restrict mode being activated on the journal: %s.") % ', '.join(INTEGRITY_HASH_LINE_FIELDS))
#                 if any(key in vals for key in ('tax_ids', 'tax_line_ids')):
#                     raise UserError(_('You cannot modify the taxes related to a posted journal item, you should reset the journal entry to draft to do so.'))

#             # Check the lock date.
#             if line.parent_state == 'posted' and any(self.env['account.move']._field_will_change(line, vals, field_name) for field_name in PROTECTED_FIELDS_LOCK_DATE):
#                 line.move_id._check_fiscalyear_lock_date()

#             # Check the tax lock date.
#             if line.parent_state == 'posted' and any(self.env['account.move']._field_will_change(line, vals, field_name) for field_name in PROTECTED_FIELDS_TAX_LOCK_DATE):
#                 line._check_tax_lock_date()

#             # Check the reconciliation.
#             if any(self.env['account.move']._field_will_change(line, vals, field_name) for field_name in PROTECTED_FIELDS_RECONCILIATION):
#                 line._check_reconciliation()

#             # Check switching receivable / payable accounts.
#             if account_to_write:
#                 account_type = line.account_id.user_type_id.type
#                 if line.move_id.is_sale_document(include_receipts=True):
#                     if (account_type == 'receivable' and account_to_write.user_type_id.type != account_type) \
#                             or (account_type != 'receivable' and account_to_write.user_type_id.type == 'receivable'):
#                         raise UserError(_("You can only set an account having the receivable type on payment terms lines for customer invoice."))
#                 if line.move_id.is_purchase_document(include_receipts=True):
#                     if (account_type == 'payable' and account_to_write.user_type_id.type != account_type) \
#                             or (account_type != 'payable' and account_to_write.user_type_id.type == 'payable'):
#                         raise UserError(_("You can only set an account having the payable type on payment terms lines for vendor bill."))

#         # Tracking stuff can be skipped for perfs using tracking_disable context key
#         if not self.env.context.get('tracking_disable', False):
#             # Get all tracked fields (without related fields because these fields must be manage on their own model)
#             tracking_fields = []
#             for value in vals:
#                 field = self._fields[value]
#                 if hasattr(field, 'related') and field.related:
#                     continue # We don't want to track related field.
#                 if hasattr(field, 'tracking') and field.tracking:
#                     tracking_fields.append(value)
#             ref_fields = self.env['account.move.line'].fields_get(tracking_fields)

#             # Get initial values for each line
#             move_initial_values = {}
#             for line in self.filtered(lambda l: l.move_id.posted_before): # Only lines with posted once move.
#                 for field in tracking_fields:
#                     # Group initial values by move_id
#                     if line.move_id.id not in move_initial_values:
#                         move_initial_values[line.move_id.id] = {}
#                     move_initial_values[line.move_id.id].update({field: line[field]})

#         result = True
#         for line in self:
#             cleaned_vals = line.move_id._cleanup_write_orm_values(line, vals)
#             if not cleaned_vals:
#                 continue

#             # Auto-fill amount_currency if working in single-currency.
#             if 'currency_id' not in cleaned_vals \
#                 and line.currency_id == line.company_currency_id \
#                 and any(field_name in cleaned_vals for field_name in ('debit', 'credit')):
#                 cleaned_vals.update({
#                     'amount_currency': vals.get('debit', 0.0) - vals.get('credit', 0.0),
#                 })

#             result |= super(AccountMoveLine, line).write(cleaned_vals)

#             if not line.move_id.is_invoice(include_receipts=True):
#                 continue

#             # Ensure consistency between accounting & business fields.
#             # As we can't express such synchronization as computed fields without cycling, we need to do it both
#             # in onchange and in create/write. So, if something changed in accounting [resp. business] fields,
#             # business [resp. accounting] fields are recomputed.
#             if any(field in cleaned_vals for field in ACCOUNTING_FIELDS):
#                 price_subtotal = line._get_price_total_and_subtotal().get('price_subtotal', 0.0)
#                 to_write = line._get_fields_onchange_balance(price_subtotal=price_subtotal)
#                 to_write.update(line._get_price_total_and_subtotal(
#                     price_unit=to_write.get('price_unit', line.price_unit),
#                     quantity=to_write.get('quantity', line.quantity),
#                     discount=to_write.get('discount', line.discount),
#                 ))
#                 result |= super(AccountMoveLine, line).write(to_write)
#             elif any(field in cleaned_vals for field in BUSINESS_FIELDS):
#                 to_write = line._get_price_total_and_subtotal()
#                 to_write.update(line._get_fields_onchange_subtotal(
#                     price_subtotal=to_write['price_subtotal'],
#                 ))
#                 result |= super(AccountMoveLine, line).write(to_write)

#         # Check total_debit == total_credit in the related moves.
#         if self._context.get('check_move_validity', True):
#             self.mapped('move_id')._check_balanced()

#         self.mapped('move_id')._synchronize_business_models({'line_ids'})

#         if not self.env.context.get('tracking_disable', False):
#             # Log changes to move lines on each move
#             for move_id, modified_lines in move_initial_values.items():
#                 for line in self.filtered(lambda l: l.move_id.id == move_id):
#                     tracking_value_ids = line._mail_track(ref_fields, modified_lines)[1]
#                     if tracking_value_ids:
#                         msg = f"{html_escape(_('Journal Item'))} <a href=# data-oe-model=account.move.line data-oe-id={line.id}>#{line.id}</a> {html_escape(_('updated'))}"
#                         line.move_id._message_log(
#                             body=msg,
#                             tracking_value_ids=tracking_value_ids
#                         )

#         return result

#     def _valid_field_parameter(self, field, name):
#         # I can't even
#         return name == 'tracking' or super()._valid_field_parameter(field, name)

#     @api.ondelete(at_uninstall=False)
#     def _unlink_except_posted(self):
#         # Prevent deleting lines on posted entries
#         if not self._context.get('force_delete') and any(m.state == 'posted' for m in self.move_id):
#             raise UserError(_('You cannot delete an item linked to a posted entry.'))

#     def unlink(self):
#         moves = self.mapped('move_id')

#         # Check the lines are not reconciled (partially or not).
#         self._check_reconciliation()

#         # Check the lock date.
#         moves._check_fiscalyear_lock_date()

#         # Check the tax lock date.
#         self._check_tax_lock_date()

#         res = super(AccountMoveLine, self).unlink()

#         # Check total_debit == total_credit in the related moves.
#         if self._context.get('check_move_validity', True):
#             moves._check_balanced()

#         return res

#     @api.model
#     def default_get(self, default_fields):
#         # OVERRIDE
#         values = super(AccountMoveLine, self).default_get(default_fields)

#         if 'account_id' in default_fields and not values.get('account_id') \
#             and (self._context.get('journal_id') or self._context.get('default_journal_id')) \
#             and self._context.get('default_move_type') in ('out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt'):
#             # Fill missing 'account_id'.
#             journal = self.env['account.journal'].browse(self._context.get('default_journal_id') or self._context['journal_id'])
#             values['account_id'] = journal.default_account_id.id
#         elif self._context.get('line_ids') and any(field_name in default_fields for field_name in ('debit', 'credit', 'account_id', 'partner_id')):
#             move = self.env['account.move'].new({'line_ids': self._context['line_ids']})

#             # Suggest default value for debit / credit to balance the journal entry.
#             balance = sum(line['debit'] - line['credit'] for line in move.line_ids)
#             # if we are here, line_ids is in context, so journal_id should also be.
#             journal = self.env['account.journal'].browse(self._context.get('default_journal_id') or self._context['journal_id'])
#             currency = journal.exists() and journal.company_id.currency_id
#             if currency:
#                 balance = currency.round(balance)
#             if balance < 0.0:
#                 values.update({'debit': -balance})
#             if balance > 0.0:
#                 values.update({'credit': balance})

#             # Suggest default value for 'partner_id'.
#             if 'partner_id' in default_fields and not values.get('partner_id'):
#                 if len(move.line_ids[-2:]) == 2 and  move.line_ids[-1].partner_id == move.line_ids[-2].partner_id != False:
#                     values['partner_id'] = move.line_ids[-2:].mapped('partner_id').id

#             # Suggest default value for 'account_id'.
#             if 'account_id' in default_fields and not values.get('account_id'):
#                 if len(move.line_ids[-2:]) == 2 and  move.line_ids[-1].account_id == move.line_ids[-2].account_id != False:
#                     values['account_id'] = move.line_ids[-2:].mapped('account_id').id
#         if values.get('display_type') or self.display_type:
#             values.pop('account_id', None)
#         return values

#     @api.depends('ref', 'move_id')
#     def name_get(self):
#         result = []
#         for line in self:
#             name = line.move_id.name or ''
#             if line.ref:
#                 name += " (%s)" % line.ref
#             name += (line.name or line.product_id.display_name) and (' ' + (line.name or line.product_id.display_name)) or ''
#             result.append((line.id, name))
#         return result

#     @api.model
#     def invalidate_cache(self, fnames=None, ids=None):
#         # Invalidate cache of related moves
#         if fnames is None or 'move_id' in fnames:
#             field = self._fields['move_id']
#             lines = self.env.cache.get_records(self, field) if ids is None else self.browse(ids)
#             move_ids = {id_ for id_ in self.env.cache.get_values(lines, field) if id_}
#             if move_ids:
#                 self.env['account.move'].invalidate_cache(ids=move_ids)
#         return super().invalidate_cache(fnames=fnames, ids=ids)

#     # -------------------------------------------------------------------------
#     # TRACKING METHODS
#     # -------------------------------------------------------------------------

#     def _mail_track(self, tracked_fields, initial):
#         changes, tracking_value_ids = super()._mail_track(tracked_fields, initial)
#         if len(changes) > len(tracking_value_ids):
#             for i, changed_field in enumerate(changes):
#                 if tracked_fields[changed_field]['type'] in ['one2many', 'many2many']:
#                     field = self.env['ir.model.fields']._get(self._name, changed_field)
#                     vals = {
#                         'field': field.id,
#                         'field_desc': field.field_description,
#                         'field_type': field.ttype,
#                         'tracking_sequence': field.tracking,
#                         'old_value_char': ', '.join(initial[changed_field].mapped('name')),
#                         'new_value_char': ', '.join(self[changed_field].mapped('name')),
#                     }
#                     tracking_value_ids.insert(i, Command.create(vals))
#         return changes, tracking_value_ids

#     # -------------------------------------------------------------------------
#     # RECONCILIATION
#     # -------------------------------------------------------------------------

#     def _prepare_reconciliation_partials(self):
#         ''' Prepare the partials on the current journal items to perform the reconciliation.
#         /!\ The order of records in self is important because the journal items will be reconciled using this order.

#         :return: A recordset of account.partial.reconcile.
#         '''
#         def fix_remaining_cent(currency, abs_residual, partial_amount):
#             if abs_residual - currency.rounding <= partial_amount <= abs_residual + currency.rounding:
#                 return abs_residual
#             else:
#                 return partial_amount

#         debit_lines = iter(self.filtered(lambda line: line.balance > 0.0 or line.amount_currency > 0.0))
#         credit_lines = iter(self.filtered(lambda line: line.balance < 0.0 or line.amount_currency < 0.0))
#         debit_line = None
#         credit_line = None

#         debit_amount_residual = 0.0
#         debit_amount_residual_currency = 0.0
#         credit_amount_residual = 0.0
#         credit_amount_residual_currency = 0.0
#         debit_line_currency = None
#         credit_line_currency = None

#         partials_vals_list = []

#         while True:

#             # Move to the next available debit line.
#             if not debit_line:
#                 debit_line = next(debit_lines, None)
#                 if not debit_line:
#                     break
#                 debit_amount_residual = debit_line.amount_residual

#                 if debit_line.currency_id:
#                     debit_amount_residual_currency = debit_line.amount_residual_currency
#                     debit_line_currency = debit_line.currency_id
#                 else:
#                     debit_amount_residual_currency = debit_amount_residual
#                     debit_line_currency = debit_line.company_currency_id

#             # Move to the next available credit line.
#             if not credit_line:
#                 credit_line = next(credit_lines, None)
#                 if not credit_line:
#                     break
#                 credit_amount_residual = credit_line.amount_residual

#                 if credit_line.currency_id:
#                     credit_amount_residual_currency = credit_line.amount_residual_currency
#                     credit_line_currency = credit_line.currency_id
#                 else:
#                     credit_amount_residual_currency = credit_amount_residual
#                     credit_line_currency = credit_line.company_currency_id

#             min_amount_residual = min(debit_amount_residual, -credit_amount_residual)
#             has_debit_residual_left = not debit_line.company_currency_id.is_zero(debit_amount_residual) and debit_amount_residual > 0.0
#             has_credit_residual_left = not credit_line.company_currency_id.is_zero(credit_amount_residual) and credit_amount_residual < 0.0
#             has_debit_residual_curr_left = not debit_line_currency.is_zero(debit_amount_residual_currency) and debit_amount_residual_currency > 0.0
#             has_credit_residual_curr_left = not credit_line_currency.is_zero(credit_amount_residual_currency) and credit_amount_residual_currency < 0.0

#             if debit_line_currency == credit_line_currency:
#                 # Reconcile on the same currency.

#                 # The debit line is now fully reconciled because:
#                 # - either amount_residual & amount_residual_currency are at 0.
#                 # - either the credit_line is not an exchange difference one.
#                 if not has_debit_residual_curr_left and (has_credit_residual_curr_left or not has_debit_residual_left):
#                     debit_line = None
#                     continue

#                 # The credit line is now fully reconciled because:
#                 # - either amount_residual & amount_residual_currency are at 0.
#                 # - either the debit is not an exchange difference one.
#                 if not has_credit_residual_curr_left and (has_debit_residual_curr_left or not has_credit_residual_left):
#                     credit_line = None
#                     continue

#                 min_amount_residual_currency = min(debit_amount_residual_currency, -credit_amount_residual_currency)
#                 min_debit_amount_residual_currency = min_amount_residual_currency
#                 min_credit_amount_residual_currency = min_amount_residual_currency

#             else:
#                 # Reconcile on the company's currency.

#                 # The debit line is now fully reconciled since amount_residual is 0.
#                 if not has_debit_residual_left:
#                     debit_line = None
#                     continue

#                 # The credit line is now fully reconciled since amount_residual is 0.
#                 if not has_credit_residual_left:
#                     credit_line = None
#                     continue

#                 min_debit_amount_residual_currency = credit_line.company_currency_id._convert(
#                     min_amount_residual,
#                     debit_line.currency_id,
#                     credit_line.company_id,
#                     credit_line.date,
#                 )
#                 min_debit_amount_residual_currency = fix_remaining_cent(
#                     debit_line.currency_id,
#                     debit_amount_residual_currency,
#                     min_debit_amount_residual_currency,
#                 )
#                 min_credit_amount_residual_currency = debit_line.company_currency_id._convert(
#                     min_amount_residual,
#                     credit_line.currency_id,
#                     debit_line.company_id,
#                     debit_line.date,
#                 )
#                 min_credit_amount_residual_currency = fix_remaining_cent(
#                     credit_line.currency_id,
#                     -credit_amount_residual_currency,
#                     min_credit_amount_residual_currency,
#                 )

#             debit_amount_residual -= min_amount_residual
#             debit_amount_residual_currency -= min_debit_amount_residual_currency
#             credit_amount_residual += min_amount_residual
#             credit_amount_residual_currency += min_credit_amount_residual_currency

#             partials_vals_list.append({
#                 'amount': min_amount_residual,
#                 'debit_amount_currency': min_debit_amount_residual_currency,
#                 'credit_amount_currency': min_credit_amount_residual_currency,
#                 'debit_move_id': debit_line.id,
#                 'credit_move_id': credit_line.id,
#             })

#         return partials_vals_list

#     def _create_exchange_difference_move(self):
#         ''' Create the exchange difference journal entry on the current journal items.
#         :return: An account.move record.
#         '''

#         def _add_lines_to_exchange_difference_vals(lines, exchange_diff_move_vals):
#             ''' Generate the exchange difference values used to create the journal items
#             in order to fix the residual amounts and add them into 'exchange_diff_move_vals'.

#             1) When reconciled on the same foreign currency, the journal items are
#             fully reconciled regarding this currency but it could be not the case
#             of the balance that is expressed using the company's currency. In that
#             case, we need to create exchange difference journal items to ensure this
#             residual amount reaches zero.

#             2) When reconciled on the company currency but having different foreign
#             currencies, the journal items are fully reconciled regarding the company
#             currency but it's not always the case for the foreign currencies. In that
#             case, the exchange difference journal items are created to ensure this
#             residual amount in foreign currency reaches zero.

#             :param lines:                   The account.move.lines to which fix the residual amounts.
#             :param exchange_diff_move_vals: The current vals of the exchange difference journal entry.
#             :return:                        A list of pair <line, sequence> to perform the reconciliation
#                                             at the creation of the exchange difference move where 'line'
#                                             is the account.move.line to which the 'sequence'-th exchange
#                                             difference line will be reconciled with.
#             '''
#             journal = self.env['account.journal'].browse(exchange_diff_move_vals['journal_id'])
#             to_reconcile = []

#             for line in lines:

#                 exchange_diff_move_vals['date'] = max(exchange_diff_move_vals['date'], line.date)

#                 if not line.company_currency_id.is_zero(line.amount_residual):
#                     # amount_residual_currency == 0 and amount_residual has to be fixed.

#                     if line.amount_residual > 0.0:
#                         exchange_line_account = journal.company_id.expense_currency_exchange_account_id
#                     else:
#                         exchange_line_account = journal.company_id.income_currency_exchange_account_id

#                 elif line.currency_id and not line.currency_id.is_zero(line.amount_residual_currency):
#                     # amount_residual == 0 and amount_residual_currency has to be fixed.

#                     if line.amount_residual_currency > 0.0:
#                         exchange_line_account = journal.company_id.expense_currency_exchange_account_id
#                     else:
#                         exchange_line_account = journal.company_id.income_currency_exchange_account_id
#                 else:
#                     continue

#                 sequence = len(exchange_diff_move_vals['line_ids'])
#                 exchange_diff_move_vals['line_ids'] += [
#                     (0, 0, {
#                         'name': _('Currency exchange rate difference'),
#                         'debit': -line.amount_residual if line.amount_residual < 0.0 else 0.0,
#                         'credit': line.amount_residual if line.amount_residual > 0.0 else 0.0,
#                         'amount_currency': -line.amount_residual_currency,
#                         'account_id': line.account_id.id,
#                         'currency_id': line.currency_id.id,
#                         'partner_id': line.partner_id.id,
#                         'sequence': sequence,
#                     }),
#                     (0, 0, {
#                         'name': _('Currency exchange rate difference'),
#                         'debit': line.amount_residual if line.amount_residual > 0.0 else 0.0,
#                         'credit': -line.amount_residual if line.amount_residual < 0.0 else 0.0,
#                         'amount_currency': line.amount_residual_currency,
#                         'account_id': exchange_line_account.id,
#                         'currency_id': line.currency_id.id,
#                         'partner_id': line.partner_id.id,
#                         'sequence': sequence + 1,
#                     }),
#                 ]

#                 to_reconcile.append((line, sequence))

#             return to_reconcile

#         def _add_cash_basis_lines_to_exchange_difference_vals(lines, exchange_diff_move_vals):
#             ''' Generate the exchange difference values used to create the journal items
#             in order to fix the cash basis lines using the transfer account in a multi-currencies
#             environment when this account is not a reconcile one.

#             When the tax cash basis journal entries are generated and all involved
#             transfer account set on taxes are all reconcilable, the account balance
#             will be reset to zero by the exchange difference journal items generated
#             above. However, this mechanism will not work if there is any transfer
#             accounts that are not reconcile and we are generating the cash basis
#             journal items in a foreign currency. In that specific case, we need to
#             generate extra journal items at the generation of the exchange difference
#             journal entry to ensure this balance is reset to zero and then, will not
#             appear on the tax report leading to erroneous tax base amount / tax amount.

#             :param lines:                   The account.move.lines to which fix the residual amounts.
#             :param exchange_diff_move_vals: The current vals of the exchange difference journal entry.
#             '''
#             for move in lines.move_id:
#                 account_vals_to_fix = {}

#                 move_values = move._collect_tax_cash_basis_values()

#                 # The cash basis doesn't need to be handle for this move because there is another payment term
#                 # line that is not yet fully paid.
#                 if not move_values or not move_values['is_fully_paid']:
#                     continue

#                 # ==========================================================================
#                 # Add the balance of all tax lines of the current move in order in order
#                 # to compute the residual amount for each of them.
#                 # ==========================================================================

#                 for caba_treatment, line in move_values['to_process_lines']:

#                     vals = {
#                         'currency_id': line.currency_id.id,
#                         'partner_id': line.partner_id.id,
#                         'tax_ids': [(6, 0, line.tax_ids.ids)],
#                         'tax_tag_ids': [(6, 0, line.tax_tag_ids.ids)],
#                         'debit': line.debit,
#                         'credit': line.credit,
#                     }

#                     if caba_treatment == 'tax' and not line.reconciled:
#                         # Tax line.
#                         grouping_key = self.env['account.partial.reconcile']._get_cash_basis_tax_line_grouping_key_from_record(line)
#                         if grouping_key in account_vals_to_fix:
#                             debit = account_vals_to_fix[grouping_key]['debit'] + vals['debit']
#                             credit = account_vals_to_fix[grouping_key]['credit'] + vals['credit']
#                             balance = debit - credit

#                             account_vals_to_fix[grouping_key].update({
#                                 'debit': balance if balance > 0 else 0,
#                                 'credit': -balance if balance < 0 else 0,
#                                 'tax_base_amount': account_vals_to_fix[grouping_key]['tax_base_amount'] + line.tax_base_amount,
#                             })
#                         else:
#                             account_vals_to_fix[grouping_key] = {
#                                 **vals,
#                                 'account_id': line.account_id.id,
#                                 'tax_base_amount': line.tax_base_amount,
#                                 'tax_repartition_line_id': line.tax_repartition_line_id.id,
#                             }
#                     elif caba_treatment == 'base':
#                         # Base line.
#                         account_to_fix = line.company_id.account_cash_basis_base_account_id
#                         if not account_to_fix:
#                             continue

#                         grouping_key = self.env['account.partial.reconcile']._get_cash_basis_base_line_grouping_key_from_record(line, account=account_to_fix)

#                         if grouping_key not in account_vals_to_fix:
#                             account_vals_to_fix[grouping_key] = {
#                                 **vals,
#                                 'account_id': account_to_fix.id,
#                             }
#                         else:
#                             # Multiple base lines could share the same key, if the same
#                             # cash basis tax is used alone on several lines of the invoices
#                             account_vals_to_fix[grouping_key]['debit'] += vals['debit']
#                             account_vals_to_fix[grouping_key]['credit'] += vals['credit']

#                 # ==========================================================================
#                 # Subtract the balance of all previously generated cash basis journal entries
#                 # in order to retrieve the residual balance of each involved transfer account.
#                 # ==========================================================================

#                 cash_basis_moves = self.env['account.move'].search([('tax_cash_basis_origin_move_id', '=', move.id)])
#                 for line in cash_basis_moves.line_ids:
#                     grouping_key = None
#                     if line.tax_repartition_line_id:
#                         # Tax line.
#                         grouping_key = self.env['account.partial.reconcile']._get_cash_basis_tax_line_grouping_key_from_record(
#                             line,
#                             account=line.tax_line_id.cash_basis_transition_account_id,
#                         )
#                     elif line.tax_ids:
#                         # Base line.
#                         grouping_key = self.env['account.partial.reconcile']._get_cash_basis_base_line_grouping_key_from_record(
#                             line,
#                             account=line.company_id.account_cash_basis_base_account_id,
#                         )

#                     if grouping_key not in account_vals_to_fix:
#                         continue

#                     account_vals_to_fix[grouping_key]['debit'] -= line.debit
#                     account_vals_to_fix[grouping_key]['credit'] -= line.credit

#                 # ==========================================================================
#                 # Generate the exchange difference journal items:
#                 # - to reset the balance of all transfer account to zero.
#                 # - fix rounding issues on the tax account/base tax account.
#                 # ==========================================================================

#                 for values in account_vals_to_fix.values():
#                     balance = values['debit'] - values['credit']

#                     if move.company_currency_id.is_zero(balance):
#                         continue

#                     if values.get('tax_repartition_line_id'):
#                         # Tax line.
#                         tax_repartition_line = self.env['account.tax.repartition.line'].browse(values['tax_repartition_line_id'])
#                         account = tax_repartition_line.account_id or self.env['account.account'].browse(values['account_id'])

#                         sequence = len(exchange_diff_move_vals['line_ids'])
#                         exchange_diff_move_vals['line_ids'] += [
#                             (0, 0, {
#                                 **values,
#                                 'name': _('Currency exchange rate difference (cash basis)'),
#                                 'debit': balance if balance > 0.0 else 0.0,
#                                 'credit': -balance if balance < 0.0 else 0.0,
#                                 'account_id': account.id,
#                                 'sequence': sequence,
#                             }),
#                             (0, 0, {
#                                 **values,
#                                 'name': _('Currency exchange rate difference (cash basis)'),
#                                 'debit': -balance if balance < 0.0 else 0.0,
#                                 'credit': balance if balance > 0.0 else 0.0,
#                                 'account_id': values['account_id'],
#                                 'tax_ids': [],
#                                 'tax_tag_ids': [],
#                                 'tax_repartition_line_id': False,
#                                 'sequence': sequence + 1,
#                             }),
#                         ]
#                     else:
#                         # Base line.
#                         sequence = len(exchange_diff_move_vals['line_ids'])
#                         exchange_diff_move_vals['line_ids'] += [
#                             (0, 0, {
#                                 **values,
#                                 'name': _('Currency exchange rate difference (cash basis)'),
#                                 'debit': balance if balance > 0.0 else 0.0,
#                                 'credit': -balance if balance < 0.0 else 0.0,
#                                 'sequence': sequence,
#                             }),
#                             (0, 0, {
#                                 **values,
#                                 'name': _('Currency exchange rate difference (cash basis)'),
#                                 'debit': -balance if balance < 0.0 else 0.0,
#                                 'credit': balance if balance > 0.0 else 0.0,
#                                 'tax_ids': [],
#                                 'tax_tag_ids': [],
#                                 'sequence': sequence + 1,
#                             }),
#                         ]

#         if not self:
#             return self.env['account.move']

#         company = self[0].company_id
#         journal = company.currency_exchange_journal_id

#         exchange_diff_move_vals = {
#             'move_type': 'entry',
#             'date': date.min,
#             'journal_id': journal.id,
#             'line_ids': [],
#         }

#         # Fix residual amounts.
#         to_reconcile = _add_lines_to_exchange_difference_vals(self, exchange_diff_move_vals)

#         # Fix cash basis entries.
#         is_cash_basis_needed = self[0].account_internal_type in ('receivable', 'payable')
#         if is_cash_basis_needed:
#             _add_cash_basis_lines_to_exchange_difference_vals(self, exchange_diff_move_vals)

#         # ==========================================================================
#         # Create move and reconcile.
#         # ==========================================================================

#         if exchange_diff_move_vals['line_ids']:
#             # Check the configuration of the exchange difference journal.
#             if not journal:
#                 raise UserError(_("You should configure the 'Exchange Gain or Loss Journal' in your company settings, to manage automatically the booking of accounting entries related to differences between exchange rates."))
#             if not journal.company_id.expense_currency_exchange_account_id:
#                 raise UserError(_("You should configure the 'Loss Exchange Rate Account' in your company settings, to manage automatically the booking of accounting entries related to differences between exchange rates."))
#             if not journal.company_id.income_currency_exchange_account_id.id:
#                 raise UserError(_("You should configure the 'Gain Exchange Rate Account' in your company settings, to manage automatically the booking of accounting entries related to differences between exchange rates."))

#             exchange_diff_move_vals['date'] = max(exchange_diff_move_vals['date'], company._get_user_fiscal_lock_date())

#             exchange_move = self.env['account.move'].create(exchange_diff_move_vals)
#         else:
#             return None

#         # Reconcile lines to the newly created exchange difference journal entry by creating more partials.
#         partials_vals_list = []
#         for source_line, sequence in to_reconcile:
#             exchange_diff_line = exchange_move.line_ids[sequence]

#             if source_line.company_currency_id.is_zero(source_line.amount_residual):
#                 exchange_field = 'amount_residual_currency'
#             else:
#                 exchange_field = 'amount_residual'

#             if exchange_diff_line[exchange_field] > 0.0:
#                 debit_line = exchange_diff_line
#                 credit_line = source_line
#             else:
#                 debit_line = source_line
#                 credit_line = exchange_diff_line

#             partials_vals_list.append({
#                 'amount': abs(source_line.amount_residual),
#                 'debit_amount_currency': abs(debit_line.amount_residual_currency),
#                 'credit_amount_currency': abs(credit_line.amount_residual_currency),
#                 'debit_move_id': debit_line.id,
#                 'credit_move_id': credit_line.id,
#             })

#         self.env['account.partial.reconcile'].create(partials_vals_list)

#         return exchange_move

#     def reconcile(self):
#         ''' Reconcile the current move lines all together.
#         :return: A dictionary representing a summary of what has been done during the reconciliation:
#                 * partials:             A recorset of all account.partial.reconcile created during the reconciliation.
#                 * full_reconcile:       An account.full.reconcile record created when there is nothing left to reconcile
#                                         in the involved lines.
#                 * tax_cash_basis_moves: An account.move recordset representing the tax cash basis journal entries.
#         '''
#         results = {}

#         if not self:
#             return results

#         # List unpaid invoices
#         not_paid_invoices = self.move_id.filtered(
#             lambda move: move.is_invoice(include_receipts=True) and move.payment_state not in ('paid', 'in_payment')
#         )

#         # ==== Check the lines can be reconciled together ====
#         company = None
#         account = None
#         for line in self:
#             if line.reconciled:
#                 raise UserError(_("You are trying to reconcile some entries that are already reconciled."))
#             if not line.account_id.reconcile and line.account_id.internal_type != 'liquidity':
#                 raise UserError(_("Account %s does not allow reconciliation. First change the configuration of this account to allow it.")
#                                 % line.account_id.display_name)
#             if line.move_id.state != 'posted':
#                 raise UserError(_('You can only reconcile posted entries.'))
#             if company is None:
#                 company = line.company_id
#             elif line.company_id != company:
#                 raise UserError(_("Entries doesn't belong to the same company: %s != %s")
#                                 % (company.display_name, line.company_id.display_name))
#             if account is None:
#                 account = line.account_id
#             elif line.account_id != account:
#                 raise UserError(_("Entries are not from the same account: %s != %s")
#                                 % (account.display_name, line.account_id.display_name))

#         sorted_lines = self.sorted(key=lambda line: (line.date_maturity or line.date, line.currency_id))

#         # ==== Collect all involved lines through the existing reconciliation ====

#         involved_lines = sorted_lines
#         involved_partials = self.env['account.partial.reconcile']
#         current_lines = involved_lines
#         current_partials = involved_partials
#         while current_lines:
#             current_partials = (current_lines.matched_debit_ids + current_lines.matched_credit_ids) - current_partials
#             involved_partials += current_partials
#             current_lines = (current_partials.debit_move_id + current_partials.credit_move_id) - current_lines
#             involved_lines += current_lines

#         # ==== Create partials ====

#         partials = self.env['account.partial.reconcile'].create(sorted_lines._prepare_reconciliation_partials())

#         # Track newly created partials.
#         results['partials'] = partials
#         involved_partials += partials

#         # ==== Create entries for cash basis taxes ====

#         is_cash_basis_needed = account.user_type_id.type in ('receivable', 'payable')
#         if is_cash_basis_needed and not self._context.get('move_reverse_cancel'):
#             tax_cash_basis_moves = partials._create_tax_cash_basis_moves()
#             results['tax_cash_basis_moves'] = tax_cash_basis_moves

#         # ==== Check if a full reconcile is needed ====

#         if involved_lines[0].currency_id and all(line.currency_id == involved_lines[0].currency_id for line in involved_lines):
#             is_full_needed = all(line.currency_id.is_zero(line.amount_residual_currency) for line in involved_lines)
#         else:
#             is_full_needed = all(line.company_currency_id.is_zero(line.amount_residual) for line in involved_lines)

#         if is_full_needed:

#             # ==== Create the exchange difference move ====

#             if self._context.get('no_exchange_difference'):
#                 exchange_move = None
#             else:
#                 exchange_move = involved_lines._create_exchange_difference_move()
#                 if exchange_move:
#                     exchange_move_lines = exchange_move.line_ids.filtered(lambda line: line.account_id == account)

#                     # Track newly created lines.
#                     involved_lines += exchange_move_lines

#                     # Track newly created partials.
#                     exchange_diff_partials = exchange_move_lines.matched_debit_ids \
#                                              + exchange_move_lines.matched_credit_ids
#                     involved_partials += exchange_diff_partials
#                     results['partials'] += exchange_diff_partials

#                     exchange_move._post(soft=False)

#             # ==== Create the full reconcile ====

#             results['full_reconcile'] = self.env['account.full.reconcile'].create({
#                 'exchange_move_id': exchange_move and exchange_move.id,
#                 'partial_reconcile_ids': [(6, 0, involved_partials.ids)],
#                 'reconciled_line_ids': [(6, 0, involved_lines.ids)],
#             })

#         # Trigger action for paid invoices
#         not_paid_invoices\
#             .filtered(lambda move: move.payment_state in ('paid', 'in_payment'))\
#             .action_invoice_paid()

#         return results

#     def remove_move_reconcile(self):
#         """ Undo a reconciliation """
#         (self.matched_debit_ids + self.matched_credit_ids).unlink()

#     def _copy_data_extend_business_fields(self, values):
#         ''' Hook allowing copying business fields under certain conditions.
#         E.g. The link to the sale order lines must be preserved in case of a refund.
#         '''
#         self.ensure_one()

#     def copy_data(self, default=None):
#         res = super(AccountMoveLine, self).copy_data(default=default)

#         for line, values in zip(self, res):
#             # Don't copy the name of a payment term line.
#             if line.move_id.is_invoice() and line.account_id.user_type_id.type in ('receivable', 'payable'):
#                 values['name'] = ''
#             # Don't copy restricted fields of notes
#             if line.display_type in ('line_section', 'line_note'):
#                 values['amount_currency'] = 0
#                 values['debit'] = 0
#                 values['credit'] = 0
#                 values['account_id'] = False
#             if self._context.get('include_business_fields'):
#                 line._copy_data_extend_business_fields(values)
#         return res

#     # -------------------------------------------------------------------------
#     # MISC
#     # -------------------------------------------------------------------------

#     def _get_analytic_tag_ids(self):
#         self.ensure_one()
#         return self.analytic_tag_ids.filtered(lambda r: not r.active_analytic_distribution).ids

#     def create_analytic_lines(self):
#         """ Create analytic items upon validation of an account.move.line having an analytic account or an analytic distribution.
#         """
#         lines_to_create_analytic_entries = self.env['account.move.line']
#         analytic_line_vals = []
#         for obj_line in self:
#             for tag in obj_line.analytic_tag_ids.filtered('active_analytic_distribution'):
#                 for distribution in tag.analytic_distribution_ids:
#                     analytic_line_vals.append(obj_line._prepare_analytic_distribution_line(distribution))
#             if obj_line.analytic_account_id:
#                 lines_to_create_analytic_entries |= obj_line

#         # create analytic entries in batch
#         if lines_to_create_analytic_entries:
#             analytic_line_vals += lines_to_create_analytic_entries._prepare_analytic_line()

#         self.env['account.analytic.line'].create(analytic_line_vals)

#     def _prepare_analytic_line(self):
#         """ Prepare the values used to create() an account.analytic.line upon validation of an account.move.line having
#             an analytic account. This method is intended to be extended in other modules.
#             :return list of values to create analytic.line
#             :rtype list
#         """
#         result = []
#         for move_line in self:
#             amount = (move_line.credit or 0.0) - (move_line.debit or 0.0)
#             default_name = move_line.name or (move_line.ref or '/' + ' -- ' + (move_line.partner_id and move_line.partner_id.name or '/'))
#             category = 'other'
#             if move_line.move_id.is_sale_document():
#                 category = 'invoice'
#             elif move_line.move_id.is_purchase_document():
#                 category = 'vendor_bill'
#             result.append({
#                 'name': default_name,
#                 'date': move_line.date,
#                 'account_id': move_line.analytic_account_id.id,
#                 'group_id': move_line.analytic_account_id.group_id.id,
#                 'tag_ids': [(6, 0, move_line._get_analytic_tag_ids())],
#                 'unit_amount': move_line.quantity,
#                 'product_id': move_line.product_id and move_line.product_id.id or False,
#                 'product_uom_id': move_line.product_uom_id and move_line.product_uom_id.id or False,
#                 'amount': amount,
#                 'general_account_id': move_line.account_id.id,
#                 'ref': move_line.ref,
#                 'move_id': move_line.id,
#                 'user_id': move_line.move_id.invoice_user_id.id or self._uid,
#                 'partner_id': move_line.partner_id.id,
#                 'company_id': move_line.analytic_account_id.company_id.id or move_line.move_id.company_id.id,
#                 'category': category,
#             })
#         return result

#     def _prepare_analytic_distribution_line(self, distribution):
#         """ Prepare the values used to create() an account.analytic.line upon validation of an account.move.line having
#             analytic tags with analytic distribution.
#         """
#         self.ensure_one()
#         amount = -self.balance * distribution.percentage / 100.0
#         default_name = self.name or (self.ref or '/' + ' -- ' + (self.partner_id and self.partner_id.name or '/'))
#         return {
#             'name': default_name,
#             'date': self.date,
#             'account_id': distribution.account_id.id,
#             'group_id': distribution.account_id.group_id.id,
#             'partner_id': self.partner_id.id,
#             'tag_ids': [(6, 0, [distribution.tag_id.id] + self._get_analytic_tag_ids())],
#             'unit_amount': self.quantity,
#             'product_id': self.product_id and self.product_id.id or False,
#             'product_uom_id': self.product_uom_id and self.product_uom_id.id or False,
#             'amount': amount,
#             'general_account_id': self.account_id.id,
#             'ref': self.ref,
#             'move_id': self.id,
#             'user_id': self.move_id.invoice_user_id.id or self._uid,
#             'company_id': distribution.account_id.company_id.id or self.env.company.id,
#         }

#     @api.model
#     def _query_get(self, domain=None):
#         self.check_access_rights('read')

#         context = dict(self._context or {})
#         domain = domain or []
#         if not isinstance(domain, (list, tuple)):
#             domain = ast.literal_eval(domain)

#         date_field = 'date'
#         if context.get('aged_balance'):
#             date_field = 'date_maturity'
#         if context.get('date_to'):
#             domain += [(date_field, '<=', context['date_to'])]
#         if context.get('date_from'):
#             if not context.get('strict_range'):
#                 domain += ['|', (date_field, '>=', context['date_from']), ('account_id.user_type_id.include_initial_balance', '=', True)]
#             elif context.get('initial_bal'):
#                 domain += [(date_field, '<', context['date_from'])]
#             else:
#                 domain += [(date_field, '>=', context['date_from'])]

#         if context.get('journal_ids'):
#             domain += [('journal_id', 'in', context['journal_ids'])]

#         state = context.get('state')
#         if state and state.lower() != 'all':
#             domain += [('parent_state', '=', state)]

#         if context.get('company_id'):
#             domain += [('company_id', '=', context['company_id'])]
#         elif context.get('allowed_company_ids'):
#             domain += [('company_id', 'in', self.env.companies.ids)]
#         else:
#             domain += [('company_id', '=', self.env.company.id)]

#         if context.get('reconcile_date'):
#             domain += ['|', ('reconciled', '=', False), '|', ('matched_debit_ids.max_date', '>', context['reconcile_date']), ('matched_credit_ids.max_date', '>', context['reconcile_date'])]

#         if context.get('account_tag_ids'):
#             domain += [('account_id.tag_ids', 'in', context['account_tag_ids'].ids)]

#         if context.get('account_ids'):
#             domain += [('account_id', 'in', context['account_ids'].ids)]

#         if context.get('analytic_tag_ids'):
#             domain += [('analytic_tag_ids', 'in', context['analytic_tag_ids'].ids)]

#         if context.get('analytic_account_ids'):
#             domain += [('analytic_account_id', 'in', context['analytic_account_ids'].ids)]

#         if context.get('partner_ids'):
#             domain += [('partner_id', 'in', context['partner_ids'].ids)]

#         if context.get('partner_categories'):
#             domain += [('partner_id.category_id', 'in', context['partner_categories'].ids)]

#         where_clause = ""
#         where_clause_params = []
#         tables = ''
#         if domain:
#             domain.append(('display_type', 'not in', ('line_section', 'line_note')))
#             domain.append(('parent_state', '!=', 'cancel'))

#             query = self._where_calc(domain)

#             # Wrap the query with 'company_id IN (...)' to avoid bypassing company access rights.
#             self._apply_ir_rules(query)

#             tables, where_clause, where_clause_params = query.get_sql()
#         return tables, where_clause, where_clause_params

#     def _reconciled_lines(self):
#         ids = []
#         for aml in self.filtered('account_id.reconcile'):
#             ids.extend([r.debit_move_id.id for r in aml.matched_debit_ids] if aml.credit > 0 else [r.credit_move_id.id for r in aml.matched_credit_ids])
#             ids.append(aml.id)
#         return ids

#     def open_reconcile_view(self):
#         action = self.env['ir.actions.act_window']._for_xml_id('account.action_account_moves_all_a')
#         ids = self._reconciled_lines()
#         action['domain'] = [('id', 'in', ids)]
#         return action

#     def action_automatic_entry(self):
#         action = self.env['ir.actions.act_window']._for_xml_id('account.account_automatic_entry_wizard_action')
#         # Force the values of the move line in the context to avoid issues
#         ctx = dict(self.env.context)
#         ctx.pop('active_id', None)
#         ctx.pop('default_journal_id', None)
#         ctx['active_ids'] = self.ids
#         ctx['active_model'] = 'account.move.line'
#         action['context'] = ctx
#         return action

#     @api.model
#     def _get_suspense_moves_domain(self):
#         return [
#             ('move_id.to_check', '=', True),
#             ('full_reconcile_id', '=', False),
#             ('statement_line_id', '!=', False),
#         ]

#     def _get_attachment_domains(self):
#         self.ensure_one()
#         domains = [[('res_model', '=', 'account.move'), ('res_id', '=', self.move_id.id)]]
#         if self.statement_id:
#             domains.append([('res_model', '=', 'account.bank.statement'), ('res_id', '=', self.statement_id.id)])
#         if self.payment_id:
#             domains.append([('res_model', '=', 'account.payment'), ('res_id', '=', self.payment_id.id)])
#         return domains
