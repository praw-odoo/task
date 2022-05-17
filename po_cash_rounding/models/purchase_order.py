from odoo import api, models, fields
from odoo.exceptions import UserError
from odoo.tools.misc import format_date, formatLang
from odoo import api, fields, models, Command, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.tools import (
    float_compare,
    date_utils,
    email_split,
    email_re,
    html_escape,
    is_html_empty,
)
from odoo.tools.misc import formatLang, format_date, get_lang

from datetime import date, timedelta
from collections import defaultdict
from contextlib import contextmanager
from itertools import zip_longest
from hashlib import sha256
from json import dumps

import ast
import json
import re
import warnings

INTEGRITY_HASH_MOVE_FIELDS = ('date', 'journal_id', 'company_id')
INTEGRITY_HASH_LINE_FIELDS = ('debit', 'credit', 'account_id', 'partner_id')

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    # tax_totals_json = fields.Char(
    #     string="Invoice Totals JSON",
    #     compute='_compute_tax_totals_json',
    #     readonly=False,
    #     help='Edit Tax amounts if you encounter rounding issues.')
    posted_before = fields.Boolean(help="Technical field for knowing if the move has been posted before", copy=False)
    date = fields.Date(
        string='Date',
        required=True,
        index=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        copy=False,
        tracking=True,
        default=fields.Date.context_today
    )
    move_type = fields.Selection(
        selection=[
            ("entry", "Journal Entry"),
            ("out_invoice", "Customer Invoice"),
            ("out_refund", "Customer Credit Note"),
            ("in_invoice", "Vendor Bill"),
            ("in_refund", "Vendor Credit Note"),
            ("out_receipt", "Sales Receipt"),
            ("in_receipt", "Purchase Receipt"),
        ],
        string="Type",
        required=True,
        store=True,
        index=True,
        readonly=True,
        tracking=True,
        default="entry",
        change_default=True,
    )

    @api.model
    def _get_default_journal(self):
        """Get the default journal.
        It could either be passed through the context using the 'default_journal_id' key containing its id,
        either be determined by the default type.
        """
        move_type = self._context.get("default_move_type", "entry")
        if move_type in self.get_sale_types(include_receipts=True):
            journal_types = ["sale"]
        elif move_type in self.get_purchase_types(include_receipts=True):
            journal_types = ["purchase"]
        else:
            journal_types = self._context.get("default_move_journal_types", ["general"])

        if self._context.get("default_journal_id"):
            journal = self.env["account.journal"].browse(
                self._context["default_journal_id"]
            )

            if move_type != "entry" and journal.type not in journal_types:
                raise UserError(
                    _(
                        "Cannot create an invoice of type %(move_type)s with a journal having %(journal_type)s as type.",
                        move_type=move_type,
                        journal_type=journal.type,
                    )
                )
        else:
            journal = self._search_default_journal(journal_types)

        return journal

    @api.model
    def _search_default_journal(self, journal_types):
        company_id = self._context.get("default_company_id", self.env.company.id)
        domain = [("company_id", "=", company_id), ("type", "in", journal_types)]

        journal = None
        if self._context.get("default_currency_id"):
            currency_domain = domain + [
                ("currency_id", "=", self._context["default_currency_id"])
            ]
            journal = self.env["account.journal"].search(currency_domain, limit=1)

        if not journal:
            journal = self.env["account.journal"].search(domain, limit=1)

        if not journal:
            company = self.env["res.company"].browse(company_id)

            error_msg = _(
                "No journal could be found in company %(company_name)s for any of those types: %(journal_types)s",
                company_name=company.display_name,
                journal_types=", ".join(journal_types),
            )
            raise UserError(error_msg)

        return journal

    journal_id = fields.Many2one(
        "account.journal",
        string="Journal",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        check_company=True,
        domain="[('id', 'in', suitable_journal_ids)]",
        default=_get_default_journal,
    )
    suitable_journal_ids = fields.Many2many('account.journal', compute='_compute_suitable_journal_ids')
    round_of_cash = fields.Many2one(
        "account.cash.rounding", string="Cash Rounding Method"
    )
    line_ids = fields.One2many(
        "purchase.order.line",
        "move_id",
        string="Journal Items",
        copy=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    invoice_filter_type_domain = fields.Char(compute='_compute_invoice_filter_type_domain',
        help="Technical field used to have a dynamic domain on journal / taxes in the form view.")
    
    @api.depends('move_type')
    def _compute_invoice_filter_type_domain(self):
        for move in self:
            if move.is_sale_document(include_receipts=True):
                move.invoice_filter_type_domain = 'sale'
            elif move.is_purchase_document(include_receipts=True):
                move.invoice_filter_type_domain = 'purchase'
            else:
                move.invoice_filter_type_domain = False

    @api.onchange("line_ids", "round_of_cash")
    def _onchange_recompute_dynamic_lines(self):
        print("\n\n _onchange_recompute_dynamic_lines")
        self._recompute_dynamic_lines()

    @api.depends('company_id', 'invoice_filter_type_domain')
    def _compute_suitable_journal_ids(self):
        for m in self:
            journal_type = m.invoice_filter_type_domain or 'general'
            company_id = m.company_id.id or self.env.company.id
            domain = [('company_id', '=', company_id), ('type', '=', journal_type)]
            m.suitable_journal_ids = self.env['account.journal'].search(domain)

    @api.onchange("tax_totals_json")
    def _onchange_tax_totals_json(self):
        super()._onchange_tax_totals_json()
        print("\n\n _onchange_tax_totals_json")
        """ This method is triggered by the tax group widget. It allows modifying the right
            move lines depending on the tax group whose amount got edited.
        """
        for move in self:
            if not move.is_invoice(include_receipts=True):
                continue

            purchase_totals = json.loads(move.tax_totals_json)
            print("\n\n purchase_totals", purchase_totals)
            for amount_by_group_list in purchase_totals["groups_by_subtotal"].values():
                print("\n\n amount_by_group_list", amount_by_group_list)
                for amount_by_group in amount_by_group_list:
                    print("\n\n amount_by_group", amount_by_group)
                    tax_lines = move.line_ids.filtered(
                        lambda line: line.tax_group_id.id
                        == amount_by_group["tax_group_id"]
                    )
                    print("\n\n tax_lines")
                    if tax_lines:
                        first_tax_line = tax_lines[0]
                        tax_group_old_amount = sum(tax_lines.mapped("amount_currency"))
                        sign = -1 if move.is_inbound() else 1
                        delta_amount = (
                            tax_group_old_amount * sign
                            - amount_by_group["tax_group_amount"]
                        )

                        if not move.currency_id.is_zero(delta_amount):
                            first_tax_line.amount_currency = (
                                first_tax_line.amount_currency - delta_amount * sign
                            )
                            # We have to trigger the on change manually because we don"t change the value of
                            # amount_currency in the view.
                            first_tax_line._onchange_amount_currency()

            move._recompute_dynamic_lines()

    @api.model
    def _cleanup_write_orm_values(self, record, vals):
        print("\n\n 5: _cleanup_write_orm_values")
        cleaned_vals = dict(vals)
        for field_name, value in vals.items():
            if not self._field_will_change(record, vals, field_name):
                del cleaned_vals[field_name]
        return cleaned_vals
    
    def _preprocess_taxes_map(self, taxes_map):
        print("\n\n 17: _preprocess_taxes_map")
        """ Useful in case we want to pre-process taxes_map """
        print("\n\n taxes_map", taxes_map)
        return taxes_map

    def get_invoice_types(self, include_receipts=False):
        return ["out_invoice", "out_refund", "in_refund", "in_invoice"] + (
            include_receipts and ["out_receipt", "in_receipt"] or []
        )

    def is_invoice(self, include_receipts=False):
        return self.move_type in self.get_invoice_types(include_receipts)

    @api.model
    def get_sale_types(self, include_receipts=False):
        return ['out_invoice', 'out_refund'] + (include_receipts and ['out_receipt'] or [])

    def is_sale_document(self, include_receipts=False):
        return self.move_type in self.get_sale_types(include_receipts)

    @api.model
    def get_purchase_types(self, include_receipts=False):
        return ['in_invoice', 'in_refund'] + (include_receipts and ['in_receipt'] or [])

    def is_purchase_document(self, include_receipts=False):
        return self.move_type in self.get_purchase_types(include_receipts)

    @api.model
    def get_inbound_types(self, include_receipts=True):
        return ['out_invoice', 'in_refund'] + (include_receipts and ['out_receipt'] or [])

    def is_inbound(self, include_receipts=True):
        return self.move_type in self.get_inbound_types(include_receipts)

    @api.model
    def get_outbound_types(self, include_receipts=True):
        return ['in_invoice', 'out_refund'] + (include_receipts and ['in_receipt'] or [])

    def is_outbound(self, include_receipts=True):
        return self.move_type in self.get_outbound_types(include_receipts)

    def _recompute_cash_rounding_lines(self):
        print("\n\n _recompute_cash_rounding_lines")
        """ Handle the cash rounding feature on invoices.

        In some countries, the smallest coins do not exist. For example, in Switzerland, there is no coin for 0.01 CHF.
        For this reason, if invoices are paid in cash, you have to round their total amount to the smallest coin that
        exists in the currency. For the CHF, the smallest coin is 0.05 CHF.

        There are two strategies for the rounding:

        1) Add a line on the invoice for the rounding: The cash rounding line is added as a new invoice line.
        2) Add the rounding in the biggest tax amount: The cash rounding line is added as a new tax line on the tax
        having the biggest balance.
        """
        self.ensure_one()
        in_draft_mode = self != self._origin
        print("\n\n in_draft_mode", in_draft_mode)

        def _compute_cash_rounding(self, total_amount_currency):
            print("\n\n _compute_cash_rounding", _compute_cash_rounding)
            """ Compute the amount differences due to the cash rounding.
            :param self:                    The current account.move record.
            :param total_amount_currency:   The invoice's total in invoice's currency.
            :return:                        The amount differences both in company's currency & invoice's currency.
            """
            print("\n\n self.currency_id", self.currency_id)
            print("\n\n total_amount_currency", total_amount_currency)
            difference = self.round_of_cash.compute_difference(
                self.currency_id, total_amount_currency
            )
            if self.currency_id == self.company_id.currency_id:
                diff_amount_currency = diff_balance = difference
            else:
                diff_amount_currency = difference
                diff_balance = self.currency_id._convert(
                    diff_amount_currency,
                    self.company_id.currency_id,
                    self.company_id,
                    self.date,
                )
                print("\n\n diff_balance", diff_balance)
            return diff_balance, diff_amount_currency

        def _apply_cash_rounding(
            self, diff_balance, diff_amount_currency, cash_rounding_line
        ):
            print("\n\n _apply_cash_rounding")
            """ Apply the cash rounding.
            :param self:                    The current account.move record.
            :param diff_balance:            The computed balance to set on the new rounding line.
            :param diff_amount_currency:    The computed amount in invoice's currency to set on the new rounding line.
            :param cash_rounding_line:      The existing cash rounding line.
            :return:                        The newly created rounding line.
            """
            rounding_line_vals = {
                "debit": diff_balance > 0.0 and diff_balance or 0.0,
                "credit": diff_balance < 0.0 and -diff_balance or 0.0,
                "quantity": 1.0,
                "amount_currency": diff_amount_currency,
                "partner_id": self.partner_id.id,
                "move_id": self.id,
                "currency_id": self.currency_id.id,
                "company_id": self.company_id.id,
                "company_currency_id": self.company_id.currency_id.id,
                "is_rounding_line": True,
                "sequence": 9999,
            }
            print("\n\n rounding_line_vals", rounding_line_vals)
            if self.round_of_cash.strategy == "biggest_tax":
                biggest_tax_line = None
                for tax_line in self.line_ids.filtered("tax_repartition_line_id"):
                    print("\n\n tax_line", tax_line)
                    if (
                        not biggest_tax_line
                        or tax_line.price_subtotal > biggest_tax_line.price_subtotal
                    ):
                        biggest_tax_line = tax_line

                # No tax found.
                if not biggest_tax_line:
                    return

                rounding_line_vals.update(
                    {
                        "name": _("%s (rounding)", biggest_tax_line.name),
                        "account_id": biggest_tax_line.account_id.id,
                        "tax_repartition_line_id": biggest_tax_line.tax_repartition_line_id.id,
                        "tax_tag_ids": [(6, 0, biggest_tax_line.tax_tag_ids.ids)],
                        "exclude_from_invoice_tab": True,
                    }
                )
                print("\n\n rounding_line_vals.update", rounding_line_vals)

            elif self.round_of_cash.strategy == "add_invoice_line":
                if diff_balance > 0.0 and self.round_of_cash.loss_account_id:
                    account_id = self.round_of_cash.loss_account_id.id
                else:
                    account_id = self.round_of_cash.profit_account_id.id
                rounding_line_vals.update(
                    {
                        "name": self.round_of_cash.name,
                        "account_id": account_id,
                    }
                )

            # Create or update the cash rounding line.
            if cash_rounding_line:
                print("\n\n cash_rounding_line", cash_rounding_line)
                cash_rounding_line.update(
                    {
                        "amount_currency": rounding_line_vals["amount_currency"],
                        "debit": rounding_line_vals["debit"],
                        "credit": rounding_line_vals["credit"],
                        "account_id": rounding_line_vals["account_id"],
                    }
                )
            else:
                create_method = (
                    in_draft_mode
                    and self.env["purchase.order.line"].new
                    or self.env["purchase.order.line"].create
                )
                cash_rounding_line = create_method(rounding_line_vals)

            if in_draft_mode:
                cash_rounding_line.update(
                    cash_rounding_line._get_fields_onchange_balance(
                        force_computation=True
                    )
                )

        existing_cash_rounding_line = self.line_ids.filtered(
            lambda line: line.is_rounding_line
        )

        # The cash rounding has been removed.
        if not self.round_of_cash:
            self.line_ids -= existing_cash_rounding_line
            return

        # The cash rounding strategy has changed.
        if self.round_of_cash and existing_cash_rounding_line:
            print("\n\n round_of_cash", self.round_of_cash)
            print("\n\n existing_cash_rounding_line", existing_cash_rounding_line)
            strategy = self.round_of_cash.strategy
            print("\n\n strategy", strategy)
            old_strategy = (
                "biggest_tax"
                if existing_cash_rounding_line.tax_line_id
                else "add_invoice_line"
            )
            print("\n\n old_strategy", old_strategy)
            if strategy != old_strategy:
                self.line_ids -= existing_cash_rounding_line
                existing_cash_rounding_line = self.env["purchase.order.line"]
                print("\n\n existing_cash_rounding_line", existing_cash_rounding_line)

        others_lines = self.line_ids.filtered(
            lambda line: line.account_id.user_type_id.type
            not in ("receivable", "payable")
        )
        print("\n\n others_lines", others_lines)
        others_lines -= existing_cash_rounding_line
        print("\n\n others_lines", others_lines)
        total_amount_currency = sum(others_lines.mapped("amount_currency"))
        print("\n\n total_amount_currency", total_amount_currency)
        diff_balance, diff_amount_currency = _compute_cash_rounding(
            self, total_amount_currency
        )
        print("\n\n diff_amount_currency", diff_amount_currency)
        print("\n\n diff_balance", diff_balance)
        # The invoice is already rounded.
        if self.currency_id.is_zero(diff_balance) and self.currency_id.is_zero(
            diff_amount_currency
        ):
            print(
                "\n\n self.currency_id.is_zero(diff_balance)",
                self.currency_id.is_zero(diff_balance),
            )
            print(
                "\n\n self.currency_id.is_zero(diff_amount_currency)",
                self.currency_id.is_zero(diff_amount_currency),
            )
            self.line_ids -= existing_cash_rounding_line
            print("\n\n existing_cash_rounding_line", existing_cash_rounding_line)
            return

        _apply_cash_rounding(
            self, diff_balance, diff_amount_currency, existing_cash_rounding_line
        )

    @api.onchange("order_line")
    def _onchange_order_line(self):
        print("\n\n order_line")
        current_invoice_lines = self.line_ids.filtered(
            lambda line: not line.exclude_from_invoice_tab
        )
        print("\n\n current_invoice_lines", current_invoice_lines)
        others_lines = self.line_ids - current_invoice_lines
        print("\n\n self.line_ids", self.line_ids)
        print("\n\n others_lines", others_lines)
        if others_lines and current_invoice_lines - self.line_ids:
            others_lines[0].recompute_tax_line = True
        self.line_ids = others_lines + self.order_line
        self._onchange_recompute_dynamic_lines()

    @api.model
    def _get_tax_grouping_key_from_tax_line(self, tax_line):
        print(
            "\n\n 14: _get_tax_grouping_key_from_tax_line",
            {
                "tax_repartition_line_id": tax_line.tax_repartition_line_id.id,
                "group_tax_id": tax_line.group_tax_id.id,
                "account_id": tax_line.account_id.id,
                "currency_id": tax_line.currency_id.id,
                "analytic_tag_ids": [
                    (
                        6,
                        0,
                        tax_line.tax_line_id.analytic
                        and tax_line.analytic_tag_ids.ids
                        or [],
                    )
                ],
                "analytic_account_id": tax_line.tax_line_id.analytic
                and tax_line.analytic_account_id.id,
                "tax_ids": [(6, 0, tax_line.tax_ids.ids)],
                "tax_tag_ids": [(6, 0, tax_line.tax_tag_ids.ids)],
                "partner_id": tax_line.partner_id.id,
            },
        )
        """ Create the dictionary based on a tax line that will be used as key to group taxes together.
        /!\ Must be consistent with '_get_tax_grouping_key_from_base_line'.
        :param tax_line:    An account.move.line being a tax line (with 'tax_repartition_line_id' set then).
        :return:            A dictionary containing all fields on which the tax will be grouped.
        """
        return {
            "tax_repartition_line_id": tax_line.tax_repartition_line_id.id,
            "group_tax_id": tax_line.group_tax_id.id,
            "account_id": tax_line.account_id.id,
            "currency_id": tax_line.currency_id.id,
            "analytic_tag_ids": [
                (
                    6,
                    0,
                    tax_line.tax_line_id.analytic
                    and tax_line.analytic_tag_ids.ids
                    or [],
                )
            ],
            "analytic_account_id": tax_line.tax_line_id.analytic
            and tax_line.analytic_account_id.id,
            "tax_ids": [(6, 0, tax_line.tax_ids.ids)],
            "tax_tag_ids": [(6, 0, tax_line.tax_tag_ids.ids)],
            "partner_id": tax_line.partner_id.id,
        }

    @api.model
    def _get_tax_grouping_key_from_base_line(self, base_line, tax_vals):
        print("\n\n 15: _get_tax_grouping_key_from_base_line")
        """ Create the dictionary based on a base line that will be used as key to group taxes together.
        /!\ Must be consistent with '_get_tax_grouping_key_from_tax_line'.
        :param base_line:   An account.move.line being a base line (that could contains something in 'tax_ids').
        :param tax_vals:    An element of compute_all(...)['taxes'].
        :return:            A dictionary containing all fields on which the tax will be grouped.
        """
        tax_repartition_line = self.env["account.tax.repartition.line"].browse(
            tax_vals["tax_repartition_line_id"]
        )
        print("\n\n tax_repartition_line", tax_repartition_line)
        account = (
            base_line._get_default_tax_account(tax_repartition_line)
            or base_line.account_id
        )
        print("\n\n account", account)
        print(
            "\n\n ",
            {
                "tax_repartition_line_id": tax_vals["tax_repartition_line_id"],
                "group_tax_id": tax_vals["group"].id if tax_vals["group"] else False,
                "account_id": account.id,
                "currency_id": base_line.currency_id.id,
                "analytic_tag_ids": [
                    (
                        6,
                        0,
                        tax_vals["analytic"] and base_line.analytic_tag_ids.ids or [],
                    )
                ],
                "analytic_account_id": tax_vals["analytic"]
                and base_line.analytic_account_id.id,
                "tax_ids": [(6, 0, tax_vals["tax_ids"])],
                "tax_tag_ids": [(6, 0, tax_vals["tag_ids"])],
                "partner_id": base_line.partner_id.id,
            },
        )
        return {
            "tax_repartition_line_id": tax_vals["tax_repartition_line_id"],
            "group_tax_id": tax_vals["group"].id if tax_vals["group"] else False,
            "account_id": account.id,
            "currency_id": base_line.currency_id.id,
            "analytic_tag_ids": [
                (6, 0, tax_vals["analytic"] and base_line.analytic_tag_ids.ids or [])
            ],
            "analytic_account_id": tax_vals["analytic"]
            and base_line.analytic_account_id.id,
            "tax_ids": [(6, 0, tax_vals["tax_ids"])],
            "tax_tag_ids": [(6, 0, tax_vals["tag_ids"])],
            "partner_id": base_line.partner_id.id,
        }

    @api.model
    def _get_base_amount_to_display(
        self, base_amount, tax_rep_ln, parent_tax_group=None
    ):
        print("\n\n 21: _get_base_amount_to_display")
        """ The base amount returned for taxes by compute_all has is the balance
        of the base line. For inbound operations, positive sign is on credit, so
        we need to invert the sign of this amount before displaying it.
        """
        source_tax = (
            parent_tax_group or tax_rep_ln.invoice_tax_id or tax_rep_ln.refund_tax_id
        )
        print("\n\n source_tax", source_tax)
        if (tax_rep_ln.invoice_tax_id and source_tax.type_tax_use == "sale") or (
            tax_rep_ln.refund_tax_id and source_tax.type_tax_use == "purchase"
        ):
            print("\n\n base_amount", base_amount)
            return -base_amount
        return base_amount

    def _recompute_tax_lines(self, recompute_tax_base_amount=False):
        print(
            "\n\n ",
        )
        """ Compute the dynamic tax lines of the journal entry.

        :param recompute_tax_base_amount: Flag forcing only the recomputation of the `tax_base_amount` field.
        """
        self.ensure_one()
        in_draft_mode = self != self._origin

        def _serialize_tax_grouping_key(grouping_dict):
            print(
                "\n\n ",
            )
            """ Serialize the dictionary values to be used in the taxes_map.
            :param grouping_dict: The values returned by '_get_tax_grouping_key_from_tax_line' or '_get_tax_grouping_key_from_base_line'.
            :return: A string representing the values.
            """
            return "-".join(str(v) for v in grouping_dict.values())

        def _compute_base_line_taxes(base_line):
            print(
                "\n\n ",
            )
            """ Compute taxes amounts both in company currency / foreign currency as the ratio between
            amount_currency & balance could not be the same as the expected currency rate.
            The 'amount_currency' value will be set on compute_all(...)['taxes'] in multi-currency.
            :param base_line:   The account.move.line owning the taxes.
            :return:            The result of the compute_all method.
            """
            move = base_line.move_id
            print(
                "\n\n ",
            )
            if move.is_invoice(include_receipts=True):
                handle_price_include = True
                sign = -1 if move.is_inbound() else 1
                quantity = base_line.quantity
                is_refund = move.move_type in ("out_refund", "in_refund")
                price_unit_wo_discount = (
                    sign * base_line.price_unit * (1 - (base_line.discount / 100.0))
                )
            else:
                handle_price_include = False
                quantity = 1.0
                tax_type = (
                    base_line.tax_ids[0].type_tax_use if base_line.tax_ids else None
                )
                is_refund = (tax_type == "sale" and base_line.debit) or (
                    tax_type == "purchase" and base_line.credit
                )
                price_unit_wo_discount = base_line.amount_currency

            return base_line.tax_ids._origin.with_context(
                force_sign=move._get_tax_force_sign()
            ).compute_all(
                price_unit_wo_discount,
                currency=base_line.currency_id,
                quantity=quantity,
                product=base_line.product_id,
                partner=base_line.partner_id,
                is_refund=is_refund,
                handle_price_include=handle_price_include,
                include_caba_tags=move.always_tax_exigible,
            )

        taxes_map = {}

        # ==== Add tax lines ====
        to_remove = self.env["purchase.order.line"]
        for line in self.line_ids.filtered("tax_repartition_line_id"):
            grouping_dict = self._get_tax_grouping_key_from_tax_line(line)
            grouping_key = _serialize_tax_grouping_key(grouping_dict)
            if grouping_key in taxes_map:
                # A line with the same key does already exist, we only need one
                # to modify it; we have to drop this one.
                to_remove += line
            else:
                taxes_map[grouping_key] = {
                    "tax_line": line,
                    "amount": 0.0,
                    "tax_base_amount": 0.0,
                    "grouping_dict": False,
                }
        if not recompute_tax_base_amount:
            self.line_ids -= to_remove

        # ==== Mount base lines ====
        for line in self.line_ids.filtered(
            lambda line: not line.tax_repartition_line_id
        ):
            # Don't call compute_all if there is no tax.
            if not line.tax_ids:
                if not recompute_tax_base_amount:
                    line.tax_tag_ids = [(5, 0, 0)]
                continue

            compute_all_vals = _compute_base_line_taxes(line)

            # Assign tags on base line
            if not recompute_tax_base_amount:
                line.tax_tag_ids = compute_all_vals["base_tags"] or [(5, 0, 0)]

            for tax_vals in compute_all_vals["taxes"]:
                grouping_dict = self._get_tax_grouping_key_from_base_line(
                    line, tax_vals
                )
                grouping_key = _serialize_tax_grouping_key(grouping_dict)

                tax_repartition_line = self.env["account.tax.repartition.line"].browse(
                    tax_vals["tax_repartition_line_id"]
                )
                tax = (
                    tax_repartition_line.invoice_tax_id
                    or tax_repartition_line.refund_tax_id
                )

                taxes_map_entry = taxes_map.setdefault(
                    grouping_key,
                    {
                        "tax_line": None,
                        "amount": 0.0,
                        "tax_base_amount": 0.0,
                        "grouping_dict": False,
                    },
                )
                taxes_map_entry["amount"] += tax_vals["amount"]
                taxes_map_entry["tax_base_amount"] += self._get_base_amount_to_display(
                    tax_vals["base"], tax_repartition_line, tax_vals["group"]
                )
                taxes_map_entry["grouping_dict"] = grouping_dict

        # ==== Pre-process taxes_map ====
        taxes_map = self._preprocess_taxes_map(taxes_map)

        # ==== Process taxes_map ====
        for taxes_map_entry in taxes_map.values():
            # The tax line is no longer used in any base lines, drop it.
            if taxes_map_entry["tax_line"] and not taxes_map_entry["grouping_dict"]:
                if not recompute_tax_base_amount:
                    self.line_ids -= taxes_map_entry["tax_line"]
                continue

            currency = self.env["res.currency"].browse(
                taxes_map_entry["grouping_dict"]["currency_id"]
            )

            # tax_base_amount field is expressed using the company currency.
            tax_base_amount = currency._convert(
                taxes_map_entry["tax_base_amount"],
                self.company_currency_id,
                self.company_id,
                self.date or fields.Date.context_today(self),
            )

            # Recompute only the tax_base_amount.
            if recompute_tax_base_amount:
                if taxes_map_entry["tax_line"]:
                    taxes_map_entry["tax_line"].tax_base_amount = tax_base_amount
                continue

            balance = currency._convert(
                taxes_map_entry["amount"],
                self.company_currency_id,
                self.company_id,
                self.date or fields.Date.context_today(self),
            )
            to_write_on_line = {
                "amount_currency": taxes_map_entry["amount"],
                "currency_id": taxes_map_entry["grouping_dict"]["currency_id"],
                "debit": balance > 0.0 and balance or 0.0,
                "credit": balance < 0.0 and -balance or 0.0,
                "tax_base_amount": tax_base_amount,
            }

            if taxes_map_entry["tax_line"]:
                # Update an existing tax line.
                taxes_map_entry["tax_line"].update(to_write_on_line)
            else:
                # Create a new tax line.
                create_method = (
                    in_draft_mode
                    and self.env["purchase.order.line"].new
                    or self.env["purchase.order.line"].create
                )
                tax_repartition_line_id = taxes_map_entry["grouping_dict"][
                    "tax_repartition_line_id"
                ]
                tax_repartition_line = self.env["account.tax.repartition.line"].browse(
                    tax_repartition_line_id
                )
                tax = (
                    tax_repartition_line.invoice_tax_id
                    or tax_repartition_line.refund_tax_id
                )
                taxes_map_entry["tax_line"] = create_method(
                    {
                        **to_write_on_line,
                        "name": tax.name,
                        "move_id": self.id,
                        "company_id": line.company_id.id,
                        "company_currency_id": line.company_currency_id.id,
                        "tax_base_amount": tax_base_amount,
                        "exclude_from_invoice_tab": True,
                        **taxes_map_entry["grouping_dict"],
                    }
                )

            if in_draft_mode:
                taxes_map_entry["tax_line"].update(
                    taxes_map_entry["tax_line"]._get_fields_onchange_balance(
                        force_computation=True
                    )
                )

    def _get_tax_force_sign(self):
        print("\n\n 16: _get_tax_force_sign")
        """ The sign must be forced to a negative sign in case the balance is on credit
            to avoid negatif taxes amount.
            Example - Customer Invoice :
            Fixed Tax  |  unit price  |   discount   |  amount_tax  | amount_total |
            -------------------------------------------------------------------------
                0.67   |      115      |     100%     |    - 0.67    |      0
            -------------------------------------------------------------------------"""
        self.ensure_one()
        print(
            "\n\n -1 if self.move_type in ('out_invoice', 'in_refund', 'out_receipt') else 1",
            -1 if self.move_type in ("out_invoice", "in_refund", "out_receipt") else 1,
        )
        return (
            -1 if self.move_type in ("out_invoice", "in_refund", "out_receipt") else 1
        )

    def _recompute_dynamic_lines(
        self, recompute_all_taxes=False, recompute_tax_base_amount=False
    ):
        print("\n\n _recompute_dynamic_lines")
        """ Recompute all lines that depend of others.

        For example, tax lines depends of base lines (lines having tax_ids set). This is also the case of cash rounding
        lines that depend of base lines or tax lines depending the cash rounding strategy. When a payment term is set,
        this method will auto-balance the move with payment term lines.

        :param recompute_all_taxes: Force the computation of taxes. If set to False, the computation will be done
                                    or not depending of the field 'recompute_tax_line' in lines.
        """
        for invoice in self:
            # Dispatch lines and pre-compute some aggregated values like taxes.
            for line in invoice.line_ids:
                if line.recompute_tax_line:
                    recompute_all_taxes = True
                    line.recompute_tax_line = False

            # Compute taxes.
            if recompute_all_taxes:
                invoice._recompute_tax_lines()
            if recompute_tax_base_amount:
                invoice._recompute_tax_lines(recompute_tax_base_amount=True)

            if invoice.is_invoice(include_receipts=True):

                # Compute cash rounding.
                invoice._recompute_cash_rounding_lines()

                # # Compute payment terms.
                invoice._recompute_payment_terms_lines()

                # # Only synchronize one2many in onchange.
                if invoice != invoice._origin:
                    invoice.order_line = invoice.line_ids.filtered(lambda line: not line.exclude_from_invoice_tab)

    def _recompute_payment_terms_lines(self):
        print("\n\n 25: _recompute_payment_terms_lines")
        """ Compute the dynamic payment term lines of the journal entry."""
        self.ensure_one()
        self = self.with_company(self.company_id)
        print("\n\n 25: self", self)
        in_draft_mode = self != self._origin
        print("\n\n 25: self", self)
        today = fields.Date.context_today(self)
        print("\n\n 25: today", today)
        self = self.with_company(self.journal_id.company_id)
        print("\n\n 25: self", self)

        def _get_payment_terms_computation_date(self):
            print("\n\n 26: _get_payment_terms_computation_date")
            """ Get the date from invoice that will be used to compute the payment terms.
            :param self:    The current account.move record.
            :return:        A datetime.date object.
            """
            if self.invoice_payment_term_id:
                print(
                    "\n\n 25: self.invoice_payment_term_id",
                    self.invoice_payment_term_id,
                )
                print("\n\n 25: self.invoice_date ", self.invoice_date)
                return self.invoice_date or today
            else:
                print("\n\n 25: self.invoice_date_due ", self.invoice_date_due)
                print("\n\n 25: self.invoice_date ", self.invoice_date)
                return self.invoice_date_due or self.invoice_date or today

        def _get_payment_terms_account(self, payment_terms_lines):
            print("\n\n 27: _get_payment_terms_account")
            """ Get the account from invoice that will be set as receivable / payable account.
            :param self:                    The current account.move record.
            :param payment_terms_lines:     The current payment terms lines.
            :return:                        An account.account record.
            """
            if payment_terms_lines:
                print("\n\n 25: payment_terms_lines ", payment_terms_lines)
                # Retrieve account from previous payment terms lines in order to allow the user to set a custom one.
                print(
                    "\n\n 25: payment_terms_lines[0].account_id ",
                    payment_terms_lines[0].account_id,
                )
                return payment_terms_lines[0].account_id
            elif self.partner_id:
                print("\n\n 25: self.partner_id ", self.partner_id)
                # Retrieve account from partner.
                if self.is_sale_document(include_receipts=True):
                    print(
                        "\n\n self.is_sale_document(include_receipts=True)",
                        self.is_sale_document(include_receipts=True),
                    )
                    print(
                        "\n\n self.partner_id.property_account_receivable_id",
                        self.partner_id.property_account_receivable_id,
                    )
                    return self.partner_id.property_account_receivable_id
                else:
                    print(
                        "\n\n self.partner_id.property_account_payable_id",
                        self.partner_id.property_account_payable_id,
                    )
                    return self.partner_id.property_account_payable_id
            else:
                # Search new account.
                domain = [
                    ("company_id", "=", self.company_id.id),
                    (
                        "internal_type",
                        "=",
                        "receivable"
                        if self.move_type
                        in ("out_invoice", "out_refund", "out_receipt")
                        else "payable",
                    ),
                ]
                print("\n\n domain", domain)
                return self.env["account.account"].search(domain, limit=1)

        def _compute_payment_terms(self, date, total_balance, total_amount_currency):
            print("\n\n 28: _compute_payment_terms")
            """ Compute the payment terms.
            :param self:                    The current account.move record.
            :param date:                    The date computed by '_get_payment_terms_computation_date'.
            :param total_balance:           The invoice's total in company's currency.
            :param total_amount_currency:   The invoice's total in invoice's currency.
            :return:                        A list <to_pay_company_currency, to_pay_invoice_currency, due_date>.
            """
            if self.invoice_payment_term_id:
                print("\n\nself.invoice_payment_term_id ", self.invoice_payment_term_id)
                to_compute = self.invoice_payment_term_id.compute(
                    total_balance, date_ref=date, currency=self.company_id.currency_id
                )
                print("\n\n to_compute", to_compute)
                if self.currency_id == self.company_id.currency_id:
                    # Single-currency.
                    print(
                        "\n\n [(b[0], b[1], b[1]) for b in to_compute]",
                        [(b[0], b[1], b[1]) for b in to_compute],
                    )
                    return [(b[0], b[1], b[1]) for b in to_compute]
                else:
                    # Multi-currencies.
                    print("\n\n to_compute_currency", to_compute_currency)
                    to_compute_currency = self.invoice_payment_term_id.compute(
                        total_amount_currency, date_ref=date, currency=self.currency_id
                    )
                    print(
                        "\n\n [(b[0], b[1], ac[1]) for b, ac in zip(to_compute, to_compute_currency)]",
                        [
                            (b[0], b[1], ac[1])
                            for b, ac in zip(to_compute, to_compute_currency)
                        ],
                    )
                    return [
                        (b[0], b[1], ac[1])
                        for b, ac in zip(to_compute, to_compute_currency)
                    ]
            else:
                return [
                    (fields.Date.to_string(date), total_balance, total_amount_currency)
                ]

        def _compute_diff_payment_terms_lines(
            self, existing_terms_lines, account, to_compute
        ):
            print("\n\n 29: _compute_diff_payment_terms_lines")
            """ Process the result of the '_compute_payment_terms' method and creates/updates corresponding invoice lines.
            :param self:                    The current account.move record.
            :param existing_terms_lines:    The current payment terms lines.
            :param account:                 The account.account record returned by '_get_payment_terms_account'.
            :param to_compute:              The list returned by '_compute_payment_terms'.
            """
            # As we try to update existing lines, sort them by due date.
            existing_terms_lines = existing_terms_lines.sorted(
                lambda line: line.date_maturity or today
            )
            print("\n\n existing_terms_lines", existing_terms_lines)
            existing_terms_lines_index = 0

            # Recompute amls: update existing line or create new one for each payment term.
            new_terms_lines = self.env["purchase.order.line"]
            print("\n\n new_terms_lines", new_terms_lines)
            for date_maturity, balance, amount_currency in to_compute:
                print("\n\n to_compute", to_compute)
                print(
                    "\n\n date_maturity, balance, amount_currency",
                    date_maturity,
                    balance,
                    amount_currency,
                )
                currency = self.journal_id.company_id.currency_id
                if currency and currency.is_zero(balance) and len(to_compute) > 1:
                    print(
                        "\n\n currency and currency.is_zero(balance) and len(to_compute) > 1",
                        currency,
                        currency.is_zero(balance),
                        len(to_compute) > 1,
                    )
                    continue

                if existing_terms_lines_index < len(existing_terms_lines):
                    print("\n\n existing_terms_lines_index", existing_terms_lines_index)
                    print("\n\n len(existing_terms_lines)", len(existing_terms_lines))
                    # Update existing line.
                    candidate = existing_terms_lines[existing_terms_lines_index]
                    print("\n\n candidate", candidate)
                    existing_terms_lines_index += 1
                    print("\n\n existing_terms_lines_index", existing_terms_lines_index)
                    candidate.update(
                        {
                            "date_maturity": date_maturity,
                            "amount_currency": -amount_currency,
                            "debit": balance < 0.0 and -balance or 0.0,
                            "credit": balance > 0.0 and balance or 0.0,
                        }
                    )
                    print("\n\n candidate", candidate)
                else:
                    # Create new line.
                    create_method = (
                        in_draft_mode
                        and self.env["purchase.order.line"].new
                        or self.env["purchase.order.line"].create
                    )
                    candidate = create_method(
                        {
                            "name": self.payment_reference or "",
                            "debit": balance < 0.0 and -balance or 0.0,
                            "credit": balance > 0.0 and balance or 0.0,
                            "quantity": 1.0,
                            "amount_currency": -amount_currency,
                            "date_maturity": date_maturity,
                            "move_id": self.id,
                            "currency_id": self.currency_id.id,
                            "account_id": account.id,
                            "partner_id": self.commercial_partner_id.id,
                            "exclude_from_invoice_tab": True,
                        }
                    )
                    print("\n\n create_method", create_method)
                    print("\n\n candidate", candidate)
                new_terms_lines += candidate
                print("\n\n new_terms_lines", new_terms_lines)
                if in_draft_mode:
                    candidate.update(
                        candidate._get_fields_onchange_balance(force_computation=True)
                    )
                    print("\n\n candidate", candidate)
            return new_terms_lines

        print("\n\n existing_terms_lines", existing_terms_lines)
        existing_terms_lines = self.line_ids.filtered(
            lambda line: line.account_id.user_type_id.type in ("receivable", "payable")
        )
        print("\n\n existing_terms_lines", existing_terms_lines)
        others_lines = self.line_ids.filtered(
            lambda line: line.account_id.user_type_id.type
            not in ("receivable", "payable")
        )
        print("\n\n others_lines", others_lines)
        company_currency_id = (self.company_id or self.env.company).currency_id
        print("\n\n company_currency_id", company_currency_id)
        total_balance = sum(
            others_lines.mapped(lambda l: company_currency_id.round(l.balance))
        )
        print("\n\n total_balance", total_balance)
        total_amount_currency = sum(others_lines.mapped("amount_currency"))
        print("\n\n total_amount_currency", total_amount_currency)
        if not others_lines:
            print("\n\n self.line_ids", self.line_ids)
            self.line_ids -= existing_terms_lines
            print("\n\n self.line_ids", self.line_ids)
            return

        computation_date = _get_payment_terms_computation_date(self)
        print("\n\n computation_date", computation_date)
        account = _get_payment_terms_account(self, existing_terms_lines)
        print("\n\n account", account)
        to_compute = _compute_payment_terms(
            self, computation_date, total_balance, total_amount_currency
        )
        print("\n\n to_compute", to_compute)
        new_terms_lines = _compute_diff_payment_terms_lines(
            self, existing_terms_lines, account, to_compute
        )
        print("\n\n new_terms_lines", new_terms_lines)
        print("\n\n self.line_ids", self.line_ids)
        # Remove old terms lines that are no longer needed.
        self.line_ids -= existing_terms_lines - new_terms_lines
        print("\n\n self.line_ids", self.line_ids)
        if new_terms_lines:

            self.payment_reference = new_terms_lines[-1].name or ""
            print("\n\n self.payment_reference", self.payment_reference)
            self.invoice_date_due = new_terms_lines[-1].date_maturity
            print("\n\n self.invoice_date_due", self.invoice_date_due)

    def onchange(self, values, field_name, field_onchange):
        print("\n\n 33: onchange")
        print("\n\n 33: values", values)
        print("\n\n 33: field_name", field_name)
        print("\n\n 33: field_onchange", field_onchange)
        # OVERRIDE
        # As the dynamic lines in this model are quite complex, we need to ensure some computations are done exactly
        # at the beginning / at the end of the onchange mechanism. So, the onchange recursivity is disabled.
        return super(PurchaseOrder, self.with_context(recursive_onchanges=False)).onchange(values, field_name, field_onchange)

    @api.depends(
        "line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched",
        "line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual",
        "line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency",
        "line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched",
        "line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual",
        "line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency",
        "line_ids.debit",
        "line_ids.credit",
        "line_ids.currency_id",
        "line_ids.amount_currency",
        "line_ids.amount_residual",
        "line_ids.amount_residual_currency",
        "line_ids.payment_id.state",
        "line_ids.full_reconcile_id",
    )
    def _payment_state_matters(self):
        ''' Determines when new_pmt_state must be upated.
        Method created to allow overrides.
        :return: Boolean '''
        self.ensure_one()
        return self.is_invoice(include_receipts=True)
    
    def _compute_amount(self):
        print("\n\n 40: _compute_amount")
        for move in self:
            print("\n\n move", move)
            if move.payment_state == "invoicing_legacy":
                print("\n\n  move.payment_state", move.payment_state)
                # invoicing_legacy state is set via SQL when setting setting field
                # invoicing_switch_threshold (defined in account_accountant).
                # The only way of going out of this state is through this setting,
                # so we don't recompute it here.
                move.payment_state = move.payment_state
                print("\n\n  move.payment_state", move.payment_state)
                continue

            total_untaxed = 0.0
            total_untaxed_currency = 0.0
            total_tax = 0.0
            total_tax_currency = 0.0
            total_to_pay = 0.0
            total_residual = 0.0
            total_residual_currency = 0.0
            total = 0.0
            total_currency = 0.0
            currencies = move._get_lines_onchange_currency().currency_id

            for line in move.line_ids:
                print("\n\n move.line_ids", move.line_ids)
                print("\n\n line", line)
                if move._payment_state_matters():
                    # === Invoices ===
                    print("\n\n move._payment_state_matters()", line)
                    if not line.exclude_from_invoice_tab:
                        print("\n\n line.exclude_from_invoice_tab",line.exclude_from_invoice_tab)
                        # Untaxed amount.
                        total_untaxed += line.balance
                        print("\n\n total_untaxed", total_untaxed)
                        total_untaxed_currency += line.amount_currency
                        print("\n\n total_untaxed_currency", total_untaxed_currency)
                        total += line.balance
                        print("\n\n line.balance", line.balance)
                        print("\n\n total", total)
                        total_currency += line.amount_currency
                        print("\n\n total_currency", total_currency)
                    elif line.tax_line_id:
                        print("\n\n line.tax_line_id", line.tax_line_id)
                        # Tax amount.
                        print("\n\n total_tax", total_tax)
                        total_tax += line.balance
                        print("\n\n total_tax", total_tax)
                        total_tax_currency += line.amount_currency
                        print("\n\n total_tax_currency", total_tax_currency)
                        total += line.balance
                        print("\n\n total", total)
                        total_currency += line.amount_currency
                        print("\n\n total_currency", total_currency)
                    elif line.account_id.user_type_id.type in ("receivable", "payable"):
                        # Residual amount.
                        total_to_pay += line.balance
                        total_residual += line.amount_residual
                        total_residual_currency += line.amount_residual_currency
                else:
                    # === Miscellaneous journal entry ===
                    if line.debit:
                        total += line.balance
                        total_currency += line.amount_currency

            if move.move_type == "entry" or move.is_outbound():
                sign = 1
            else:
                sign = -1
            move.amount_untaxed = sign * (
                total_untaxed_currency if len(currencies) == 1 else total_untaxed
            )
            move.amount_tax = sign * (
                total_tax_currency if len(currencies) == 1 else total_tax
            )
            move.amount_total = sign * (
                total_currency if len(currencies) == 1 else total
            )
            move.amount_residual = -sign * (
                total_residual_currency if len(currencies) == 1 else total_residual
            )
            move.amount_untaxed_signed = -total_untaxed
            move.amount_tax_signed = -total_tax
            move.amount_total_signed = (
                abs(total) if move.move_type == "entry" else -total
            )
            move.amount_residual_signed = total_residual
            move.amount_total_in_currency_signed = (
                abs(move.amount_total)
                if move.move_type == "entry"
                else -(sign * move.amount_total)
            )

            currency = (
                currencies if len(currencies) == 1 else move.company_id.currency_id
            )

            # Compute 'payment_state'.
            new_pmt_state = "not_paid" if move.move_type != "entry" else False

            if move._payment_state_matters() and move.state == "posted":
                if currency.is_zero(move.amount_residual):
                    reconciled_payments = move._get_reconciled_payments()
                    if not reconciled_payments or all(
                        payment.is_matched for payment in reconciled_payments
                    ):
                        new_pmt_state = "paid"
                    else:
                        new_pmt_state = move._get_invoice_in_payment_state()
                elif currency.compare_amounts(total_to_pay, total_residual) != 0:
                    new_pmt_state = "partial"

            if new_pmt_state == "paid" and move.move_type in (
                "in_invoice",
                "out_invoice",
                "entry",
            ):
                reverse_type = (
                    move.move_type == "in_invoice"
                    and "in_refund"
                    or move.move_type == "out_invoice"
                    and "out_refund"
                    or "entry"
                )
                reverse_moves = self.env["account.move"].search(
                    [
                        ("reversed_entry_id", "=", move.id),
                        ("state", "=", "posted"),
                        ("move_type", "=", reverse_type),
                    ]
                )

                # We only set 'reversed' state in cas of 1 to 1 full reconciliation with a reverse entry; otherwise, we use the regular 'paid' state
                reverse_moves_full_recs = reverse_moves.mapped(
                    "line_ids.full_reconcile_id"
                )
                if (
                    reverse_moves_full_recs.mapped(
                        "reconciled_line_ids.move_id"
                    ).filtered(
                        lambda x: x
                        not in (
                            reverse_moves
                            + reverse_moves_full_recs.mapped("exchange_move_id")
                        )
                    )
                    == move
                ):
                    new_pmt_state = "reversed"

            move.payment_state = new_pmt_state

    @api.depends(
        "line_ids.amount_currency",
        "line_ids.tax_base_amount",
        "line_ids.tax_line_id",
        "partner_id",
        "currency_id",
        "amount_total",
        "amount_untaxed",
    )
    # def _compute_tax_totals_json(self):
    #     print("\n\n 42: _compute_tax_totals_json")
    #     """ Computed field used for custom widget's rendering.
    #         Only set on invoices.
    #     """
    #     for move in self:
    #         if not move.is_invoice(include_receipts=True):
    #             # Non-invoice moves don't support that field (because of multicurrency: all lines of the invoice share the same currency)
    #             move.tax_totals_json = None
    #             continue

    #         tax_lines_data = move._prepare_tax_lines_data_for_totals_from_invoice()

    #         move.tax_totals_json = json.dumps(
    #             {
    #                 **self._get_tax_totals(
    #                     move.partner_id,
    #                     tax_lines_data,
    #                     move.amount_total,
    #                     move.amount_untaxed,
    #                     move.currency_id,
    #                 ),
    #                 "allow_tax_edition": move.is_purchase_document(
    #                     include_receipts=False
    #                 )
    #                 and move.state == "draft",
    #             }
    #         )

    def _prepare_tax_lines_data_for_totals_from_invoice(
        self, tax_line_id_filter=None, tax_ids_filter=None
    ):
        print("\n\n 43: _prepare_tax_lines_data_for_totals_from_invoice")
        """ Prepares data to be passed as tax_lines_data parameter of _get_tax_totals() from an invoice.

            NOTE: tax_line_id_filter and tax_ids_filter are used in l10n_latam to restrict the taxes with consider
                  in the totals.

            :param tax_line_id_filter: a function(aml, tax) returning true if tax should be considered on tax move line aml.
            :param tax_ids_filter: a function(aml, taxes) returning true if taxes should be considered on base move line aml.

            :return: A list of dict in the format described in _get_tax_totals's tax_lines_data's docstring.
        """
        self.ensure_one()

        tax_line_id_filter = tax_line_id_filter or (lambda aml, tax: True)
        tax_ids_filter = tax_ids_filter or (lambda aml, tax: True)

        balance_multiplicator = -1 if self.is_inbound() else 1
        tax_lines_data = []

        for line in self.line_ids:
            if line.tax_line_id and tax_line_id_filter(line, line.tax_line_id):
                tax_lines_data.append(
                    {
                        "line_key": "tax_line_%s" % line.id,
                        "tax_amount": line.amount_currency * balance_multiplicator,
                        "tax": line.tax_line_id,
                    }
                )

            if line.tax_ids:
                for base_tax in line.tax_ids.flatten_taxes_hierarchy():
                    if tax_ids_filter(line, base_tax):
                        tax_lines_data.append(
                            {
                                "line_key": "base_line_%s" % line.id,
                                "base_amount": line.amount_currency
                                * balance_multiplicator,
                                "tax": base_tax,
                                "tax_affecting_base": line.tax_line_id,
                            }
                        )

        return tax_lines_data

    @api.model
    def _prepare_tax_lines_data_for_totals_from_object(
        self, object_lines, tax_results_function
    ):
        print("\n\n 43: _prepare_tax_lines_data_for_totals_from_object")
        """ Prepares data to be passed as tax_lines_data parameter of _get_tax_totals() from any
            object using taxes. This helper is intended for purchase.order and sale.order, as a common
            function centralizing their behavior.

            :param object_lines: A list of records corresponding to the sub-objects generating the tax totals
                                 (sale.order.line or purchase.order.line, for example)

            :param tax_results_function: A function to be called to get the results of the tax computation for a
                                         line in object_lines. It takes the object line as its only parameter
                                         and returns a dict in the same format as account.tax's compute_all
                                         (most probably after calling it with the right parameters).

            :return: A list of dict in the format described in _get_tax_totals's tax_lines_data's docstring.
        """
        tax_lines_data = []

        for line in object_lines:
            tax_results = tax_results_function(line)

            for tax_result in tax_results["taxes"]:
                current_tax = self.env["account.tax"].browse(tax_result["id"])

                # Tax line
                tax_lines_data.append(
                    {
                        "line_key": f"tax_line_{line.id}_{tax_result['id']}",
                        "tax_amount": tax_result["amount"],
                        "tax": current_tax,
                    }
                )

                # Base for this tax line
                tax_lines_data.append(
                    {
                        "line_key": "base_line_%s" % line.id,
                        "base_amount": tax_results["total_excluded"],
                        "tax": current_tax,
                    }
                )

                # Base for the taxes whose base is affected by this tax line
                if tax_result["tax_ids"]:
                    affected_taxes = self.env["account.tax"].browse(
                        tax_result["tax_ids"]
                    )
                    for affected_tax in affected_taxes:
                        tax_lines_data.append(
                            {
                                "line_key": "affecting_base_line_%s_%s"
                                % (line.id, tax_result["id"]),
                                "base_amount": tax_result["amount"],
                                "tax": affected_tax,
                                "tax_affecting_base": current_tax,
                            }
                        )

        return tax_lines_data

    @api.model
    def _get_tax_totals(
        self, partner, tax_lines_data, amount_total, amount_untaxed, currency
    ):
        print("\n\n 44: _get_tax_totals")
        """ Compute the tax totals for the provided data.

        :param partner:        The partner to compute totals for
        :param tax_lines_data: All the data about the base and tax lines as a list of dictionaries.
                               Each dictionary represents an amount that needs to be added to either a tax base or amount.
                               A tax amount looks like:
                                   {
                                       'line_key':             unique identifier,
                                       'tax_amount':           the amount computed for this tax
                                       'tax':                  the account.tax object this tax line was made from
                                   }
                               For base amounts:
                                   {
                                       'line_key':             unique identifier,
                                       'base_amount':          the amount to add to the base of the tax
                                       'tax':                  the tax basing itself on this amount
                                       'tax_affecting_base':   (optional key) the tax whose tax line is having the impact
                                                               denoted by 'base_amount' on the base of the tax, in case of taxes
                                                               affecting the base of subsequent ones.
                                   }
        :param amount_total:   Total amount, with taxes.
        :param amount_untaxed: Total amount without taxes.
        :param currency:       The currency in which the amounts are computed.

        :return: A dictionary in the following form:
            {
                'amount_total':                              The total amount to be displayed on the document, including every total types.
                'amount_untaxed':                            The untaxed amount to be displayed on the document.
                'formatted_amount_total':                    Same as amount_total, but as a string formatted accordingly with partner's locale.
                'formatted_amount_untaxed':                  Same as amount_untaxed, but as a string formatted accordingly with partner's locale.
                'allow_tax_edition':                         True if the user should have the ability to manually edit the tax amounts by group
                                                             to fix rounding errors.
                'groups_by_subtotals':                       A dictionary formed liked {'subtotal': groups_data}
                                                             Where total_type is a subtotal name defined on a tax group, or the default one: 'Untaxed Amount'.
                                                             And groups_data is a list of dict in the following form:
                                                                {
                                                                    'tax_group_name':                  The name of the tax groups this total is made for.
                                                                    'tax_group_amount':                The total tax amount in this tax group.
                                                                    'tax_group_base_amount':           The base amount for this tax group.
                                                                    'formatted_tax_group_amount':      Same as tax_group_amount, but as a string
                                                                                                       formatted accordingly with partner's locale.
                                                                    'formatted_tax_group_base_amount': Same as tax_group_base_amount, but as a string
                                                                                                       formatted accordingly with partner's locale.
                                                                    'tax_group_id':                    The id of the tax group corresponding to this dict.
                                                                    'group_key':                       A unique key identifying this total dict,
                                                                }
                'subtotals':                                 A list of dictionaries in the following form, one for each subtotal in groups_by_subtotals' keys
                                                                {
                                                                    'name':                            The name of the subtotal
                                                                    'amount':                          The total amount for this subtotal, summing all
                                                                                                       the tax groups belonging to preceding subtotals and the base amount
                                                                    'formatted_amount':                Same as amount, but as a string
                                                                                                       formatted accordingly with partner's locale.
                                                                }
            }
        """
        account_tax = self.env["account.tax"]

        grouped_taxes = defaultdict(
            lambda: defaultdict(
                lambda: {"base_amount": 0.0, "tax_amount": 0.0, "base_line_keys": set()}
            )
        )
        subtotal_priorities = {}
        for line_data in tax_lines_data:
            tax_group = line_data["tax"].tax_group_id

            # Update subtotals priorities
            if tax_group.preceding_subtotal:
                subtotal_title = tax_group.preceding_subtotal
                new_priority = tax_group.sequence
            else:
                # When needed, the default subtotal is always the most prioritary
                subtotal_title = _("Untaxed Amount")
                new_priority = 0

            if (
                subtotal_title not in subtotal_priorities
                or new_priority < subtotal_priorities[subtotal_title]
            ):
                subtotal_priorities[subtotal_title] = new_priority

            # Update tax data
            tax_group_vals = grouped_taxes[subtotal_title][tax_group]

            if "base_amount" in line_data:
                # Base line
                if (
                    tax_group
                    == line_data.get("tax_affecting_base", account_tax).tax_group_id
                ):
                    # In case the base has a tax_line_id belonging to the same group as the base tax,
                    # the base for the group will be computed by the base tax's original line (the one with tax_ids and no tax_line_id)
                    continue

                if line_data["line_key"] not in tax_group_vals["base_line_keys"]:
                    # If the base line hasn't been taken into account yet, at its amount to the base total.
                    tax_group_vals["base_line_keys"].add(line_data["line_key"])
                    tax_group_vals["base_amount"] += line_data["base_amount"]

            else:
                # Tax line
                tax_group_vals["tax_amount"] += line_data["tax_amount"]

        # Compute groups_by_subtotal
        groups_by_subtotal = {}
        for subtotal_title, groups in grouped_taxes.items():
            groups_vals = [
                {
                    "tax_group_name": group.name,
                    "tax_group_amount": amounts["tax_amount"],
                    "tax_group_base_amount": amounts["base_amount"],
                    "formatted_tax_group_amount": formatLang(
                        self.env, amounts["tax_amount"], currency_obj=currency
                    ),
                    "formatted_tax_group_base_amount": formatLang(
                        self.env, amounts["base_amount"], currency_obj=currency
                    ),
                    "tax_group_id": group.id,
                    "group_key": "%s-%s" % (subtotal_title, group.id),
                }
                for group, amounts in sorted(
                    groups.items(), key=lambda l: l[0].sequence
                )
            ]

            groups_by_subtotal[subtotal_title] = groups_vals

        # Compute subtotals
        subtotals_list = []  # List, so that we preserve their order
        previous_subtotals_tax_amount = 0
        for subtotal_title in sorted(
            (sub for sub in subtotal_priorities), key=lambda x: subtotal_priorities[x]
        ):
            subtotal_value = amount_untaxed + previous_subtotals_tax_amount
            subtotals_list.append(
                {
                    "name": subtotal_title,
                    "amount": subtotal_value,
                    "formatted_amount": formatLang(
                        self.env, subtotal_value, currency_obj=currency
                    ),
                }
            )

            subtotal_tax_amount = sum(
                group_val["tax_group_amount"]
                for group_val in groups_by_subtotal[subtotal_title]
            )
            previous_subtotals_tax_amount += subtotal_tax_amount

        # Assign json-formatted result to the field
        return {
            "amount_total": amount_total,
            "amount_untaxed": amount_untaxed,
            "formatted_amount_total": formatLang(
                self.env, amount_total, currency_obj=currency
            ),
            "formatted_amount_untaxed": formatLang(
                self.env, amount_untaxed, currency_obj=currency
            ),
            "groups_by_subtotal": groups_by_subtotal,
            "subtotals": subtotals_list,
            "allow_tax_edition": False,
        }

    @api.model
    def _field_will_change(self, record, vals, field_name):
        print("\n\n 4: _field_will_change")
        if field_name not in vals:
            return False
        field = record._fields[field_name]
        if field.type == 'many2one':
            return record[field_name].id != vals[field_name]
        if field.type == 'many2many':
            current_ids = set(record[field_name].ids)
            after_write_ids = set(record.new({field_name: vals[field_name]})[field_name].ids)
            return current_ids != after_write_ids
        if field.type == 'one2many':
            return True
        if field.type == 'monetary' and record[field.get_currency_field(record)]:
            return not record[field.get_currency_field(record)].is_zero(record[field_name] - vals[field_name])
        if field.type == 'float':
            record_value = field.convert_to_cache(record[field_name], record)
            to_write_value = field.convert_to_cache(vals[field_name], record)
            return record_value != to_write_value
        return record[field_name] != vals[field_name]