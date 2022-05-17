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

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"
    parent_state = fields.Selection(related='move_id.state', store=True, readonly=True)
    exclude_from_invoice_tab = fields.Boolean(help="Technical field used to exclude some lines from the invoice_line_ids tab in the form view.")
    @api.model
    def _get_tax_exigible_domain(self):
        """Returns a domain to be used to identify the move lines that are allowed
        to be taken into account in the tax report.
        """
        return [
            # Lines on moves without any payable or receivable line are always exigible
            "|",
            ("move_id.always_tax_exigible", "=", True),
            # Lines with only tags are always exigible
            "|",
            "&",
            ("tax_line_id", "=", False),
            ("taxes_id", "=", False),
            # Lines from CABA entries are always exigible
            "|",
            ("move_id.tax_cash_basis_rec_id", "!=", False),
            # Lines from non-CABA taxes are always exigible
            "|",
            ("tax_line_id.tax_exigibility", "!=", "on_payment"),
            (
                "taxes_id.tax_exigibility",
                "!=",
                "on_payment",
            ),  # So: exigible if at least one tax from taxes_id isn't on_payment
        ]

    @api.depends(
        "tax_repartition_line_id.invoice_tax_id",
        "tax_repartition_line_id.refund_tax_id",
    )
    def _compute_tax_line_id(self):
        """tax_line_id is computed as the tax linked to the repartition line creating
        the move.
        """
        for record in self:
            rep_line = record.tax_repartition_line_id
            # A constraint on account.tax.repartition.line ensures both those fields are mutually exclusive
            record.tax_line_id = rep_line.invoice_tax_id or rep_line.refund_tax_id

    @api.constrains("account_id", "taxes_id", "tax_line_id", "reconciled")
    def _check_off_balance(self):
        for line in self:
            if line.account_id.internal_group == "off_balance":
                if any(
                    a.internal_group != line.account_id.internal_group
                    for a in line.move_id.line_ids.account_id
                ):
                    raise UserError(
                        _(
                            'If you want to use "Off-Balance Sheet" accounts, all the accounts of the journal entry must be of this type'
                        )
                    )
                if line.taxes_id or line.tax_line_id:
                    raise UserError(
                        _("You cannot use taxes on lines with an Off-Balance account")
                    )
                if line.reconciled:
                    raise UserError(
                        _(
                            'Lines from "Off-Balance Sheet" accounts cannot be reconciled'
                        )
                    )

    def _affect_tax_report(self):
        self.ensure_one()
        return (
            self.taxes_id
            or self.tax_line_id
            or self.tax_tag_ids.filtered(lambda x: x.applicability == "taxes")
        )

    def write(self, vals):
        # OVERRIDE
        ACCOUNTING_FIELDS = ("debit", "credit", "amount_currency")
        BUSINESS_FIELDS = ("price_unit", "quantity", "discount", "taxes_id")
        PROTECTED_FIELDS_TAX_LOCK_DATE = [
            "debit",
            "credit",
            "tax_line_id",
            "taxes_id",
            "tax_tag_ids",
        ]
        PROTECTED_FIELDS_LOCK_DATE = PROTECTED_FIELDS_TAX_LOCK_DATE + [
            "account_id",
            "journal_id",
            "amount_currency",
            "currency_id",
            "partner_id",
        ]
        PROTECTED_FIELDS_RECONCILIATION = (
            "account_id",
            "date",
            "debit",
            "credit",
            "amount_currency",
            "currency_id",
        )

        account_to_write = (
            self.env["account.account"].browse(vals["account_id"])
            if "account_id" in vals
            else None
        )

        # Check writing a deprecated account.
        if account_to_write and account_to_write.deprecated:
            raise UserError(_("You cannot use a deprecated account."))

        for line in self:
            if line.parent_state == "posted":
                if line.move_id.restrict_mode_hash_table and set(vals).intersection(
                    INTEGRITY_HASH_LINE_FIELDS
                ):
                    raise UserError(
                        _(
                            "You cannot edit the following fields due to restrict mode being activated on the journal: %s."
                        )
                        % ", ".join(INTEGRITY_HASH_LINE_FIELDS)
                    )
                if any(key in vals for key in ("taxes_id", "tax_line_ids")):
                    raise UserError(
                        _(
                            "You cannot modify the taxes related to a posted journal item, you should reset the journal entry to draft to do so."
                        )
                    )

            # Check the lock date.
            if line.parent_state == "posted" and any(
                self.env["purchase.order"]._field_will_change(line, vals, field_name)
                for field_name in PROTECTED_FIELDS_LOCK_DATE
            ):
                line.move_id._check_fiscalyear_lock_date()

            # Check the tax lock date.
            if line.parent_state == "posted" and any(
                self.env["purchase.order"]._field_will_change(line, vals, field_name)
                for field_name in PROTECTED_FIELDS_TAX_LOCK_DATE
            ):
                line._check_tax_lock_date()

            # Check the reconciliation.
            if any(
                self.env["purchase.order"]._field_will_change(line, vals, field_name)
                for field_name in PROTECTED_FIELDS_RECONCILIATION
            ):
                line._check_reconciliation()

            # Check switching receivable / payable accounts.
            if account_to_write:
                account_type = line.account_id.user_type_id.type
                if line.move_id.is_sale_document(include_receipts=True):
                    if (
                        account_type == "receivable"
                        and account_to_write.user_type_id.type != account_type
                    ) or (
                        account_type != "receivable"
                        and account_to_write.user_type_id.type == "receivable"
                    ):
                        raise UserError(
                            _(
                                "You can only set an account having the receivable type on payment terms lines for customer invoice."
                            )
                        )
                if line.move_id.is_purchase_document(include_receipts=True):
                    if (
                        account_type == "payable"
                        and account_to_write.user_type_id.type != account_type
                    ) or (
                        account_type != "payable"
                        and account_to_write.user_type_id.type == "payable"
                    ):
                        raise UserError(
                            _(
                                "You can only set an account having the payable type on payment terms lines for vendor bill."
                            )
                        )

        # Tracking stuff can be skipped for perfs using tracking_disable context key
        if not self.env.context.get("tracking_disable", False):
            # Get all tracked fields (without related fields because these fields must be manage on their own model)
            tracking_fields = []
            for value in vals:
                field = self._fields[value]
                if hasattr(field, "related") and field.related:
                    continue  # We don't want to track related field.
                if hasattr(field, "tracking") and field.tracking:
                    tracking_fields.append(value)
            ref_fields = self.env["purchase.order.line"].fields_get(tracking_fields)

            # Get initial values for each line
            move_initial_values = {}
            for line in self.filtered(
                lambda l: l.move_id.posted_before
            ):  # Only lines with posted once move.
                for field in tracking_fields:
                    # Group initial values by move_id
                    if line.move_id.id not in move_initial_values:
                        move_initial_values[line.move_id.id] = {}
                    move_initial_values[line.move_id.id].update({field: line[field]})

        result = True
        for line in self:
            cleaned_vals = line.move_id._cleanup_write_orm_values(line, vals)
            if not cleaned_vals:
                continue

            # Auto-fill amount_currency if working in single-currency.
            if (
                "currency_id" not in cleaned_vals
                and line.currency_id == line.company_currency_id
                and any(
                    field_name in cleaned_vals for field_name in ("debit", "credit")
                )
            ):
                cleaned_vals.update(
                    {
                        "amount_currency": vals.get("debit", 0.0)
                        - vals.get("credit", 0.0),
                    }
                )

            result |= super(PurchaseOrderLine, line).write(cleaned_vals)

            if not line.move_id.is_invoice(include_receipts=True):
                continue

            # Ensure consistency between accounting & business fields.
            # As we can't express such synchronization as computed fields without cycling, we need to do it both
            # in onchange and in create/write. So, if something changed in accounting [resp. business] fields,
            # business [resp. accounting] fields are recomputed.
            if any(field in cleaned_vals for field in ACCOUNTING_FIELDS):
                price_subtotal = line._get_price_total_and_subtotal().get(
                    "price_subtotal", 0.0
                )
                to_write = line._get_fields_onchange_balance(
                    price_subtotal=price_subtotal
                )
                to_write.update(
                    line._get_price_total_and_subtotal(
                        price_unit=to_write.get("price_unit", line.price_unit),
                        quantity=to_write.get("quantity", line.quantity),
                        discount=to_write.get("discount", line.discount),
                    )
                )
                result |= super(PurchaseOrderLine, line).write(to_write)
            elif any(field in cleaned_vals for field in BUSINESS_FIELDS):
                to_write = line._get_price_total_and_subtotal()
                to_write.update(
                    line._get_fields_onchange_subtotal(
                        price_subtotal=to_write["price_subtotal"],
                    )
                )
                result |= super(PurchaseOrderLine, line).write(to_write)

        # Check total_debit == total_credit in the related moves.
        if self._context.get("check_move_validity", True):
            self.mapped("move_id")._check_balanced()

        self.mapped("move_id")._synchronize_business_models({"line_ids"})

        if not self.env.context.get("tracking_disable", False):
            # Log changes to move lines on each move
            for move_id, modified_lines in move_initial_values.items():
                for line in self.filtered(lambda l: l.move_id.id == move_id):
                    tracking_value_ids = line._mail_track(ref_fields, modified_lines)[1]
                    if tracking_value_ids:
                        msg = f"{html_escape(_('Journal Item'))} <a href=# data-oe-model=purchase.order.line data-oe-id={line.id}>#{line.id}</a> {html_escape(_('updated'))}"
                        line.move_id._message_log(
                            body=msg, tracking_value_ids=tracking_value_ids
                        )

        return result

    def _create_exchange_difference_move(self):
        """Create the exchange difference journal entry on the current journal items.
        :return: An purchase.order record.
        """

        def _add_lines_to_exchange_difference_vals(lines, exchange_diff_move_vals):
            """Generate the exchange difference values used to create the journal items
            in order to fix the residual amounts and add them into 'exchange_diff_move_vals'.

            1) When reconciled on the same foreign currency, the journal items are
            fully reconciled regarding this currency but it could be not the case
            of the balance that is expressed using the company's currency. In that
            case, we need to create exchange difference journal items to ensure this
            residual amount reaches zero.

            2) When reconciled on the company currency but having different foreign
            currencies, the journal items are fully reconciled regarding the company
            currency but it's not always the case for the foreign currencies. In that
            case, the exchange difference journal items are created to ensure this
            residual amount in foreign currency reaches zero.

            :param lines:                   The purchase.order.lines to which fix the residual amounts.
            :param exchange_diff_move_vals: The current vals of the exchange difference journal entry.
            :return:                        A list of pair <line, sequence> to perform the reconciliation
                                            at the creation of the exchange difference move where 'line'
                                            is the purchase.order.line to which the 'sequence'-th exchange
                                            difference line will be reconciled with.
            """
            journal = self.env["account.journal"].browse(
                exchange_diff_move_vals["journal_id"]
            )
            to_reconcile = []

            for line in lines:

                exchange_diff_move_vals["date"] = max(
                    exchange_diff_move_vals["date"], line.date
                )

                if not line.company_currency_id.is_zero(line.amount_residual):
                    # amount_residual_currency == 0 and amount_residual has to be fixed.

                    if line.amount_residual > 0.0:
                        exchange_line_account = (
                            journal.company_id.expense_currency_exchange_account_id
                        )
                    else:
                        exchange_line_account = (
                            journal.company_id.income_currency_exchange_account_id
                        )

                elif line.currency_id and not line.currency_id.is_zero(
                    line.amount_residual_currency
                ):
                    # amount_residual == 0 and amount_residual_currency has to be fixed.

                    if line.amount_residual_currency > 0.0:
                        exchange_line_account = (
                            journal.company_id.expense_currency_exchange_account_id
                        )
                    else:
                        exchange_line_account = (
                            journal.company_id.income_currency_exchange_account_id
                        )
                else:
                    continue

                sequence = len(exchange_diff_move_vals["line_ids"])
                exchange_diff_move_vals["line_ids"] += [
                    (
                        0,
                        0,
                        {
                            "name": _("Currency exchange rate difference"),
                            "debit": -line.amount_residual
                            if line.amount_residual < 0.0
                            else 0.0,
                            "credit": line.amount_residual
                            if line.amount_residual > 0.0
                            else 0.0,
                            "amount_currency": -line.amount_residual_currency,
                            "account_id": line.account_id.id,
                            "currency_id": line.currency_id.id,
                            "partner_id": line.partner_id.id,
                            "sequence": sequence,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": _("Currency exchange rate difference"),
                            "debit": line.amount_residual
                            if line.amount_residual > 0.0
                            else 0.0,
                            "credit": -line.amount_residual
                            if line.amount_residual < 0.0
                            else 0.0,
                            "amount_currency": line.amount_residual_currency,
                            "account_id": exchange_line_account.id,
                            "currency_id": line.currency_id.id,
                            "partner_id": line.partner_id.id,
                            "sequence": sequence + 1,
                        },
                    ),
                ]

                to_reconcile.append((line, sequence))

            return to_reconcile

        def _add_cash_basis_lines_to_exchange_difference_vals(
            lines, exchange_diff_move_vals
        ):
            """Generate the exchange difference values used to create the journal items
            in order to fix the cash basis lines using the transfer account in a multi-currencies
            environment when this account is not a reconcile one.

            When the tax cash basis journal entries are generated and all involved
            transfer account set on taxes are all reconcilable, the account balance
            will be reset to zero by the exchange difference journal items generated
            above. However, this mechanism will not work if there is any transfer
            accounts that are not reconcile and we are generating the cash basis
            journal items in a foreign currency. In that specific case, we need to
            generate extra journal items at the generation of the exchange difference
            journal entry to ensure this balance is reset to zero and then, will not
            appear on the tax report leading to erroneous tax base amount / tax amount.

            :param lines:                   The purchase.order.lines to which fix the residual amounts.
            :param exchange_diff_move_vals: The current vals of the exchange difference journal entry.
            """
            for move in lines.move_id:
                account_vals_to_fix = {}

                move_values = move._collect_tax_cash_basis_values()

                # The cash basis doesn't need to be handle for this move because there is another payment term
                # line that is not yet fully paid.
                if not move_values or not move_values["is_fully_paid"]:
                    continue

                # ==========================================================================
                # Add the balance of all tax lines of the current move in order in order
                # to compute the residual amount for each of them.
                # ==========================================================================

                for caba_treatment, line in move_values["to_process_lines"]:

                    vals = {
                        "currency_id": line.currency_id.id,
                        "partner_id": line.partner_id.id,
                        "taxes_id": [(6, 0, line.taxes_id.ids)],
                        "tax_tag_ids": [(6, 0, line.tax_tag_ids.ids)],
                        "debit": line.debit,
                        "credit": line.credit,
                    }

                    if caba_treatment == "tax" and not line.reconciled:
                        # Tax line.
                        grouping_key = self.env[
                            "account.partial.reconcile"
                        ]._get_cash_basis_tax_line_grouping_key_from_record(line)
                        if grouping_key in account_vals_to_fix:
                            debit = (
                                account_vals_to_fix[grouping_key]["debit"]
                                + vals["debit"]
                            )
                            credit = (
                                account_vals_to_fix[grouping_key]["credit"]
                                + vals["credit"]
                            )
                            balance = debit - credit

                            account_vals_to_fix[grouping_key].update(
                                {
                                    "debit": balance if balance > 0 else 0,
                                    "credit": -balance if balance < 0 else 0,
                                    "tax_base_amount": account_vals_to_fix[
                                        grouping_key
                                    ]["tax_base_amount"]
                                    + line.tax_base_amount,
                                }
                            )
                        else:
                            account_vals_to_fix[grouping_key] = {
                                **vals,
                                "account_id": line.account_id.id,
                                "tax_base_amount": line.tax_base_amount,
                                "tax_repartition_line_id": line.tax_repartition_line_id.id,
                            }
                    elif caba_treatment == "base":
                        # Base line.
                        account_to_fix = (
                            line.company_id.account_cash_basis_base_account_id
                        )
                        if not account_to_fix:
                            continue

                        grouping_key = self.env[
                            "account.partial.reconcile"
                        ]._get_cash_basis_base_line_grouping_key_from_record(
                            line, account=account_to_fix
                        )

                        if grouping_key not in account_vals_to_fix:
                            account_vals_to_fix[grouping_key] = {
                                **vals,
                                "account_id": account_to_fix.id,
                            }
                        else:
                            # Multiple base lines could share the same key, if the same
                            # cash basis tax is used alone on several lines of the invoices
                            account_vals_to_fix[grouping_key]["debit"] += vals["debit"]
                            account_vals_to_fix[grouping_key]["credit"] += vals[
                                "credit"
                            ]

                # ==========================================================================
                # Subtract the balance of all previously generated cash basis journal entries
                # in order to retrieve the residual balance of each involved transfer account.
                # ==========================================================================

                cash_basis_moves = self.env["purchase.order"].search(
                    [("tax_cash_basis_origin_move_id", "=", move.id)]
                )
                for line in cash_basis_moves.line_ids:
                    grouping_key = None
                    if line.tax_repartition_line_id:
                        # Tax line.
                        grouping_key = self.env[
                            "account.partial.reconcile"
                        ]._get_cash_basis_tax_line_grouping_key_from_record(
                            line,
                            account=line.tax_line_id.cash_basis_transition_account_id,
                        )
                    elif line.taxes_id:
                        # Base line.
                        grouping_key = self.env[
                            "account.partial.reconcile"
                        ]._get_cash_basis_base_line_grouping_key_from_record(
                            line,
                            account=line.company_id.account_cash_basis_base_account_id,
                        )

                    if grouping_key not in account_vals_to_fix:
                        continue

                    account_vals_to_fix[grouping_key]["debit"] -= line.debit
                    account_vals_to_fix[grouping_key]["credit"] -= line.credit

                # ==========================================================================
                # Generate the exchange difference journal items:
                # - to reset the balance of all transfer account to zero.
                # - fix rounding issues on the tax account/base tax account.
                # ==========================================================================

                for values in account_vals_to_fix.values():
                    balance = values["debit"] - values["credit"]

                    if move.company_currency_id.is_zero(balance):
                        continue

                    if values.get("tax_repartition_line_id"):
                        # Tax line.
                        tax_repartition_line = self.env[
                            "account.tax.repartition.line"
                        ].browse(values["tax_repartition_line_id"])
                        account = tax_repartition_line.account_id or self.env[
                            "account.account"
                        ].browse(values["account_id"])

                        sequence = len(exchange_diff_move_vals["line_ids"])
                        exchange_diff_move_vals["line_ids"] += [
                            (
                                0,
                                0,
                                {
                                    **values,
                                    "name": _(
                                        "Currency exchange rate difference (cash basis)"
                                    ),
                                    "debit": balance if balance > 0.0 else 0.0,
                                    "credit": -balance if balance < 0.0 else 0.0,
                                    "account_id": account.id,
                                    "sequence": sequence,
                                },
                            ),
                            (
                                0,
                                0,
                                {
                                    **values,
                                    "name": _(
                                        "Currency exchange rate difference (cash basis)"
                                    ),
                                    "debit": -balance if balance < 0.0 else 0.0,
                                    "credit": balance if balance > 0.0 else 0.0,
                                    "account_id": values["account_id"],
                                    "taxes_id": [],
                                    "tax_tag_ids": [],
                                    "tax_repartition_line_id": False,
                                    "sequence": sequence + 1,
                                },
                            ),
                        ]
                    else:
                        # Base line.
                        sequence = len(exchange_diff_move_vals["line_ids"])
                        exchange_diff_move_vals["line_ids"] += [
                            (
                                0,
                                0,
                                {
                                    **values,
                                    "name": _(
                                        "Currency exchange rate difference (cash basis)"
                                    ),
                                    "debit": balance if balance > 0.0 else 0.0,
                                    "credit": -balance if balance < 0.0 else 0.0,
                                    "sequence": sequence,
                                },
                            ),
                            (
                                0,
                                0,
                                {
                                    **values,
                                    "name": _(
                                        "Currency exchange rate difference (cash basis)"
                                    ),
                                    "debit": -balance if balance < 0.0 else 0.0,
                                    "credit": balance if balance > 0.0 else 0.0,
                                    "taxes_id": [],
                                    "tax_tag_ids": [],
                                    "sequence": sequence + 1,
                                },
                            ),
                        ]

        if not self:
            return self.env["purchase.order"]

        company = self[0].company_id
        journal = company.currency_exchange_journal_id

        exchange_diff_move_vals = {
            "move_type": "entry",
            "date": date.min,
            "journal_id": journal.id,
            "line_ids": [],
        }

        # Fix residual amounts.
        to_reconcile = _add_lines_to_exchange_difference_vals(
            self, exchange_diff_move_vals
        )

        # Fix cash basis entries.
        is_cash_basis_needed = self[0].account_internal_type in (
            "receivable",
            "payable",
        )
        if is_cash_basis_needed:
            _add_cash_basis_lines_to_exchange_difference_vals(
                self, exchange_diff_move_vals
            )

        # ==========================================================================
        # Create move and reconcile.
        # ==========================================================================

        if exchange_diff_move_vals["line_ids"]:
            # Check the configuration of the exchange difference journal.
            if not journal:
                raise UserError(
                    _(
                        "You should configure the 'Exchange Gain or Loss Journal' in your company settings, to manage automatically the booking of accounting entries related to differences between exchange rates."
                    )
                )
            if not journal.company_id.expense_currency_exchange_account_id:
                raise UserError(
                    _(
                        "You should configure the 'Loss Exchange Rate Account' in your company settings, to manage automatically the booking of accounting entries related to differences between exchange rates."
                    )
                )
            if not journal.company_id.income_currency_exchange_account_id.id:
                raise UserError(
                    _(
                        "You should configure the 'Gain Exchange Rate Account' in your company settings, to manage automatically the booking of accounting entries related to differences between exchange rates."
                    )
                )

            exchange_diff_move_vals["date"] = max(
                exchange_diff_move_vals["date"], company._get_user_fiscal_lock_date()
            )

            exchange_move = self.env["purchase.order"].create(exchange_diff_move_vals)
        else:
            return None

        # Reconcile lines to the newly created exchange difference journal entry by creating more partials.
        partials_vals_list = []
        for source_line, sequence in to_reconcile:
            exchange_diff_line = exchange_move.line_ids[sequence]

            if source_line.company_currency_id.is_zero(source_line.amount_residual):
                exchange_field = "amount_residual_currency"
            else:
                exchange_field = "amount_residual"

            if exchange_diff_line[exchange_field] > 0.0:
                debit_line = exchange_diff_line
                credit_line = source_line
            else:
                debit_line = source_line
                credit_line = exchange_diff_line

            partials_vals_list.append(
                {
                    "amount": abs(source_line.amount_residual),
                    "debit_amount_currency": abs(debit_line.amount_residual_currency),
                    "credit_amount_currency": abs(credit_line.amount_residual_currency),
                    "debit_move_id": debit_line.id,
                    "credit_move_id": credit_line.id,
                }
            )

        self.env["account.partial.reconcile"].create(partials_vals_list)

        return exchange_move

    exclude_from_invoice_tab = fields.Boolean(
        help="Technical field used to exclude some lines from the invoice_line_ids tab in the form view."
    )
    tax_line_id = fields.Many2one(
        "account.tax",
        string="Originator Tax",
        ondelete="restrict",
        store=True,
        compute="_compute_tax_line_id",
        help="Indicates that this journal item is a tax line",
    )
    tax_group_id = fields.Many2one(
        related="tax_line_id.tax_group_id",
        string="Originator tax group",
        readonly=True,
        store=True,
        help="technical field for widget tax-group-custom-field",
    )
    date = fields.Date(
        related="move_id.date",
        store=True,
        readonly=True,
        index=True,
        copy=False,
        group_operator="min",
    )

    amount_currency = fields.Monetary(
        string="Amount in Currency",
        store=True,
        copy=True,
        help="The amount expressed in an optional other currency if it is a multi-currency entry.",
    )

    move_id = fields.Many2one(
        "purchase.order",
        string="Journal Entry",
        index=True,
        required=True,
        readonly=True,
        auto_join=True,
        ondelete="cascade",
        check_company=True,
        help="The move of this entry line.",
    )

    tax_repartition_line_id = fields.Many2one(
        comodel_name="account.tax.repartition.line",
        string="Originator Tax Distribution Line",
        ondelete="restrict",
        readonly=True,
        check_company=True,
        help="Tax distribution line that caused the creation of this move line, if any",
    )
    # taxes_id = fields.Many2many(
    #     comodel_name='account.tax',
    #     string="Taxes",
    #     context={'active_test': False},
    #     check_company=True,
    #     help="Taxes that apply on the base amount")
    
    recompute_tax_line = fields.Boolean(
        store=False,
        readonly=True,
        help="Technical field used to know on which lines the taxes must be recomputed.",
    )

    display_type = fields.Selection(
        [
            ("line_section", "Section"),
            ("line_note", "Note"),
        ],
        default=False,
        help="Technical field for UX purpose.",
    )
    is_rounding_line = fields.Boolean(help="Technical field used to retrieve the cash rounding line.")
    account_id = fields.Many2one(
        "account.account",
        string="Account",
        index=True,
        ondelete="cascade",
        domain="[('deprecated', '=', False), ('company_id', '=', 'company_id'),('is_off_balance', '=', False)]",
        check_company=True,
        tracking=True,
    )
    company_id = fields.Many2one(
        related="move_id.company_id", store=True, readonly=True
    )
    journal_id = fields.Many2one(
        related="move_id.journal_id", store=True, index=True, copy=False
    )
    name = fields.Char(string="Label", tracking=True)
    tax_base_amount = fields.Monetary(
        string="Base Amount",
        store=True,
        readonly=True,
        currency_field="company_currency_id",
    )
    company_currency_id = fields.Many2one(
        related="company_id.currency_id",
        string="Company Currency",
        readonly=True,
        store=True,
        help="Utility field to express amount currency",
    )

    debit = fields.Monetary(
        string="Debit", default=0.0, currency_field="company_currency_id"
    )

    credit = fields.Monetary(
        string="Credit", default=0.0, currency_field="company_currency_id"
    )

    tax_tag_ids = fields.Many2many(
        string="Tags",
        comodel_name="account.account.tag",
        ondelete="restrict",
        help="Tags assigned to this line by the tax creating it, if any. It determines its impact on financial reports.",
        tracking=True,
    )

    _sql_constraints = [
        (
            "check_credit_debit",
            "CHECK(credit + debit>=0 AND credit * debit=0)",
            "Wrong credit or debit value in accounting entry !",
        ),
        (
            "check_accountable_required_fields",
            "CHECK(COALESCE(display_type IN ('line_section', 'line_note'), 'f') OR account_id IS NOT NULL)",
            "Missing required account on accountable invoice line.",
        ),
        (
            "check_non_accountable_fields_null",
            "CHECK(display_type NOT IN ('line_section', 'line_note') OR (amount_currency = 0 AND debit = 0 AND credit = 0 AND account_id IS NULL))",
            "Forbidden unit price, account and quantity on non-accountable invoice line",
        ),
        (
            "check_amount_currency_balance_sign",
            """CHECK(
                (
                    (currency_id != company_currency_id)
                    AND
                    (
                        (debit - credit <= 0 AND amount_currency <= 0)
                        OR
                        (debit - credit >= 0 AND amount_currency >= 0)
                    )
                )
                OR
                (
                    currency_id = company_currency_id
                    AND
                    ROUND(debit - credit - amount_currency, 2) = 0
                )
            )""",
            "The amount expressed in the secondary currency must be positive when account is debited and negative when "
            "account is credited. If the currency is the same as the one from the company, this amount must strictly "
            "be equal to the balance.",
        ),
    ]

    # @api.onchange('amount_currency')
    # def _onchange_amount_currency(self):
    #     for line in self:
    #         company = line.move_id.company_id
    #         balance = line.currency_id._convert(line.amount_currency, company.currency_id, company, line.move_id.date or fields.Date.context_today(line))
    #         line.debit = balance if balance > 0.0 else 0.0
    #         line.credit = -balance if balance < 0.0 else 0.0

    #         if not line.move_id.is_invoice(include_receipts=True):
    #             continue

    #         line.update(line._get_fields_onchange_balance())
    #         line.update(line._get_price_total_and_subtotal())

    # @api.onchange('currency_id')
    # def _onchange_currency(self):
    #     for line in self:
    #         company = line.move_id.company_id

    #         if line.move_id.is_invoice(include_receipts=True):
    #             line._onchange_price_subtotal()
    #         elif not line.move_id.reversed_entry_id:
    #             balance = line.currency_id._convert(line.amount_currency, company.currency_id, company, line.move_id.date or fields.Date.context_today(line))
    #             line.debit = balance if balance > 0.0 else 0.0
    #             line.credit = -balance if balance < 0.0 else 0.0

    @api.model
    def _get_default_line_name(self, document, amount, currency, date, partner=None):
        """Helper to construct a default label to set on journal items.

        E.g. Vendor Reimbursement $ 1,555.00 - Azure Interior - 05/14/2020.

        :param document:    A string representing the type of the document.
        :param amount:      The document's amount.
        :param currency:    The document's currency.
        :param date:        The document's date.
        :param partner:     The optional partner.
        :return:            A string.
        """
        values = [
            "%s %s" % (document, formatLang(self.env, amount, currency_obj=currency))
        ]
        if partner:
            values.append(partner.display_name)
        values.append(format_date(self.env, fields.Date.to_string(date)))
        return " - ".join(values)

    @api.onchange(
        "amount_currency",
        "currency_id",
        "debit",
        "credit",
        "taxes_id",
        "account_id",
        "price_unit",
        "quantity",
    )
    def _onchange_mark_recompute_taxes(self):
        """Recompute the dynamic onchange based on taxes.
        If the edited line is a tax line, don't recompute anything as the user must be able to
        set a custom value.
        """
        for line in self:
            if not line.tax_repartition_line_id:
                line.recompute_tax_line = True

    def _get_computed_taxes(self):
        self.ensure_one()

        if self.move_id.is_sale_document(include_receipts=True):
            # Out invoice.
            if self.product_id.taxes_id:
                tax_ids = self.product_id.taxes_id.filtered(lambda tax: tax.company_id == self.move_id.company_id)
            elif self.account_id.tax_ids:
                tax_ids = self.account_id.tax_ids
            else:
                tax_ids = self.env['account.tax']
            if not tax_ids and not self.exclude_from_invoice_tab:
                tax_ids = self.move_id.company_id.account_sale_tax_id
        elif self.move_id.is_purchase_document(include_receipts=True):
            # In invoice.
            if self.product_id.supplier_taxes_id:
                tax_ids = self.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == self.move_id.company_id)
            elif self.account_id.tax_ids:
                tax_ids = self.account_id.tax_ids
            else:
                tax_ids = self.env['account.tax']
            if not tax_ids and not self.exclude_from_invoice_tab:
                tax_ids = self.move_id.company_id.account_purchase_tax_id
        else:
            # Miscellaneous operation.
            tax_ids = self.account_id.tax_ids

        if self.company_id and tax_ids:
            tax_ids = tax_ids.filtered(lambda tax: tax.company_id == self.company_id)

        return tax_ids

    @api.onchange("account_id")
    def _onchange_account_id(self):
        """Recompute 'taxes_id' based on 'account_id'.
        /!\ Don't remove existing taxes if there is no explicit taxes set on the account.
        """
        for line in self:
            if not line.display_type and (line.account_id.tax_ids or not line.taxes_id):
                taxes = line._get_computed_taxes()

                if taxes and line.move_id.fiscal_position_id:
                    taxes = line.move_id.fiscal_position_id.map_tax(taxes)

                line.taxes_id = taxes

    @api.onchange("debit")
    def _onchange_debit(self):
        if self.debit:
            self.credit = 0.0
        self._onchange_balance()

    @api.onchange("credit")
    def _onchange_credit(self):
        if self.credit:
            self.debit = 0.0
        self._onchange_balance()

    @api.onchange("amount_currency")
    def _onchange_amount_currency(self):
        for line in self:
            company = line.move_id.company_id
            balance = line.currency_id._convert(
                line.amount_currency,
                company.currency_id,
                company,
                line.move_id.date or fields.Date.context_today(line),
            )
            line.debit = balance if balance > 0.0 else 0.0
            line.credit = -balance if balance < 0.0 else 0.0

            if not line.move_id.is_invoice(include_receipts=True):
                continue

            line.update(line._get_fields_onchange_balance())
            line.update(line._get_price_total_and_subtotal())

    @api.onchange("quantity", "discount", "price_unit", "taxes_id")
    def _onchange_price_subtotal(self):
        for line in self:
            if not line.move_id.is_invoice(include_receipts=True):
                continue

            line.update(line._get_price_total_and_subtotal())
            line.update(line._get_fields_onchange_subtotal())

    # @api.model
    # def _prepare_add_missing_fields(self, values):
    #     """Deduce missing required fields from the onchange"""
    #     res = {}
    #     onchange_fields = [
    #         "name",
    #         "price_unit",
    #         "product_qty",
    #         "product_uom",
    #         "taxes_id",
    #         "date_planned",
    #     ]
    #     if (
    #         values.get("order_id")
    #         and values.get("product_id")
    #         and any(f not in values for f in onchange_fields)
    #     ):
    #         line = self.new(values)
    #         line.onchange_product_id()
    #         for field in onchange_fields:
    #             if field not in values:
    #                 res[field] = line._fields[field].convert_to_write(line[field], line)
    #     return res

    @api.model
    def default_get(self, default_fields):
        print("\n\n pol 53:")
        # OVERRIDE
        values = super(PurchaseOrderLine, self).default_get(default_fields)

        if 'account_id' in default_fields and not values.get('account_id') \
            and (self._context.get('journal_id') or self._context.get('default_journal_id')) \
            and self._context.get('default_move_type') in ('out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt'):
            # Fill missing 'account_id'.
            journal = self.env['account.journal'].browse(self._context.get('default_journal_id') or self._context['journal_id'])
            values['account_id'] = journal.default_account_id.id
        elif self._context.get('line_ids') and any(field_name in default_fields for field_name in ('debit', 'credit', 'account_id', 'partner_id')):
            move = self.env['purchase.order'].new({'line_ids': self._context['line_ids']})

            # Suggest default value for debit / credit to balance the journal entry.
            balance = sum(line['debit'] - line['credit'] for line in move.line_ids)
            # if we are here, line_ids is in context, so journal_id should also be.
            journal = self.env['account.journal'].browse(self._context.get('default_journal_id') or self._context['journal_id'])
            currency = journal.exists() and journal.company_id.currency_id
            if currency:
                balance = currency.round(balance)
            if balance < 0.0:
                values.update({'debit': -balance})
            if balance > 0.0:
                values.update({'credit': balance})

            # Suggest default value for 'partner_id'.
            if 'partner_id' in default_fields and not values.get('partner_id'):
                if len(move.line_ids[-2:]) == 2 and  move.line_ids[-1].partner_id == move.line_ids[-2].partner_id != False:
                    values['partner_id'] = move.line_ids[-2:].mapped('partner_id').id

            # Suggest default value for 'account_id'.
            if 'account_id' in default_fields and not values.get('account_id'):
                if len(move.line_ids[-2:]) == 2 and  move.line_ids[-1].account_id == move.line_ids[-2].account_id != False:
                    values['account_id'] = move.line_ids[-2:].mapped('account_id').id
        if values.get('display_type') or self.display_type:
            values.pop('account_id', None)
        return values
    
    def _get_price_total_and_subtotal(self, price_unit=None, quantity=None, discount=None, currency=None, product=None, partner=None, taxes=None, move_type=None):
        print("\n\n pol 11:")
        self.ensure_one()
        return self._get_price_total_and_subtotal_model(
            price_unit=price_unit or self.price_unit,
            quantity=quantity or self.quantity,
            discount=discount or self.discount,
            currency=currency or self.currency_id,
            product=product or self.product_id,
            partner=partner or self.partner_id,
            taxes=taxes or self.taxes_id,
            move_type=move_type or self.move_id.move_type,
        )
    
    @api.model
    def _get_price_total_and_subtotal_model(self, price_unit, quantity, discount, currency, product, partner, taxes, move_type):
        print("\n\n pol 12:")
        ''' This method is used to compute 'price_total' & 'price_subtotal'.

        :param price_unit:  The current price unit.
        :param quantity:    The current quantity.
        :param discount:    The current discount.
        :param currency:    The line's currency.
        :param product:     The line's product.
        :param partner:     The line's partner.
        :param taxes:       The applied taxes.
        :param move_type:   The type of the move.
        :return:            A dictionary containing 'price_subtotal' & 'price_total'.
        '''
        res = {}

        # Compute 'price_subtotal'.
        line_discount_price_unit = price_unit * (1 - (discount / 100.0))
        subtotal = quantity * line_discount_price_unit

        # Compute 'price_total'.
        if taxes:
            taxes_res = taxes._origin.with_context(force_sign=1).compute_all(line_discount_price_unit,
                quantity=quantity, currency=currency, product=product, partner=partner, is_refund=move_type in ('out_refund', 'in_refund'))
            res['price_subtotal'] = taxes_res['total_excluded']
            res['price_total'] = taxes_res['total_included']
        else:
            res['price_total'] = res['price_subtotal'] = subtotal
        #In case of multi currency, round before it's use for computing debit credit
        if currency:
            res = {k: currency.round(v) for k, v in res.items()}
        return res
    
    def _get_fields_onchange_subtotal(self, price_subtotal=None, move_type=None, currency=None, company=None, date=None):
        print("\n\n pol 13:")
        self.ensure_one()
        return self._get_fields_onchange_subtotal_model(
            price_subtotal=price_subtotal or self.price_subtotal,
            move_type=move_type or self.move_id.move_type,
            currency=currency or self.currency_id,
            company=company or self.move_id.company_id,
            date=date or self.move_id.date,
        )
    
    @api.model
    def _get_fields_onchange_subtotal_model(self, price_subtotal, move_type, currency, company, date):
        print("\n\n pol 14:")
        ''' This method is used to recompute the values of 'amount_currency', 'debit', 'credit' due to a change made
        in some business fields (affecting the 'price_subtotal' field).

        :param price_subtotal:  The untaxed amount.
        :param move_type:       The type of the move.
        :param currency:        The line's currency.
        :param company:         The move's company.
        :param date:            The move's date.
        :return:                A dictionary containing 'debit', 'credit', 'amount_currency'.
        '''
        if move_type in self.move_id.get_outbound_types():
            sign = 1
        elif move_type in self.move_id.get_inbound_types():
            sign = -1
        else:
            sign = 1

        amount_currency = price_subtotal * sign
        balance = currency._convert(amount_currency, company.currency_id, company, date or fields.Date.context_today(self))
        return {
            'amount_currency': amount_currency,
            'currency_id': currency.id,
            'debit': balance > 0.0 and balance or 0.0,
            'credit': balance < 0.0 and -balance or 0.0,
        }
    
    @api.onchange('debit')
    def _onchange_debit(self):
        print("\n\n pol 26:")
        if self.debit:
            self.credit = 0.0
        self._onchange_balance()

    @api.onchange('credit')
    def _onchange_credit(self):
        print("\n\n pol 27:")
        if self.credit:
            self.debit = 0.0
        self._onchange_balance()
    
    def _onchange_balance(self):
        print("\n\n pol 25:")
        for line in self:
            if line.currency_id == line.move_id.company_id.currency_id:
                line.amount_currency = line.balance
            else:
                continue
            if not line.move_id.is_invoice(include_receipts=True):
                continue
            line.update(line._get_fields_onchange_balance())
    
    @api.depends('move_id.move_type', 'taxes_id', 'tax_repartition_line_id', 'debit', 'credit', 'tax_tag_ids')
    def _compute_tax_tag_invert(self):
        print("\n\n pol 38:")
        for record in self:
            if not record.tax_repartition_line_id and not record.taxes_id :
                # Invoices imported from other softwares might only have kept the tags, not the taxes.
                record.tax_tag_invert = record.tax_tag_ids and record.move_id.is_inbound()

            elif record.move_id.move_type == 'entry':
                # For misc operations, cash basis entries and write-offs from the bank reconciliation widget
                rep_line = record.tax_repartition_line_id
                if rep_line:
                    tax_type = (rep_line.refund_tax_id or rep_line.invoice_tax_id).type_tax_use
                    is_refund = bool(rep_line.refund_tax_id)
                elif record.taxes_id:
                    tax_type = record.taxes_id[0].type_tax_use
                    is_refund = (tax_type == 'sale' and record.debit) or (tax_type == 'purchase' and record.credit)

                record.tax_tag_invert = (tax_type == 'purchase' and is_refund) or (tax_type == 'sale' and not is_refund)

            else:
                # For invoices with taxes
                record.tax_tag_invert = record.move_id.is_inbound()
    
    def _get_fields_onchange_balance(self, quantity=None, discount=None, amount_currency=None, move_type=None, currency=None, taxes=None, price_subtotal=None, force_computation=False):
        print("\n\n pol 15:")
        self.ensure_one()
        return self._get_fields_onchange_balance_model(
            quantity=quantity or self.quantity,
            discount=discount or self.discount,
            amount_currency=amount_currency or self.amount_currency,
            move_type=move_type or self.move_id.move_type,
            currency=currency or self.currency_id or self.move_id.currency_id,
            taxes=taxes or self.taxes_id,
            price_subtotal=price_subtotal or self.price_subtotal,
            force_computation=force_computation,
        )

    @api.model
    def _get_fields_onchange_balance_model(self, quantity, discount, amount_currency, move_type, currency, taxes, price_subtotal, force_computation=False):
        print("\n\n pol 16:")
        ''' This method is used to recompute the values of 'quantity', 'discount', 'price_unit' due to a change made
        in some accounting fields such as 'balance'.

        This method is a bit complex as we need to handle some special cases.
        For example, setting a positive balance with a 100% discount.

        :param quantity:        The current quantity.
        :param discount:        The current discount.
        :param amount_currency: The new balance in line's currency.
        :param move_type:       The type of the move.
        :param currency:        The currency.
        :param taxes:           The applied taxes.
        :param price_subtotal:  The price_subtotal.
        :return:                A dictionary containing 'quantity', 'discount', 'price_unit'.
        '''
        if move_type in self.move_id.get_outbound_types():
            sign = 1
        elif move_type in self.move_id.get_inbound_types():
            sign = -1
        else:
            sign = 1
        amount_currency *= sign

        # Avoid rounding issue when dealing with price included taxes. For example, when the price_unit is 2300.0 and
        # a 5.5% price included tax is applied on it, a balance of 2300.0 / 1.055 = 2180.094 ~ 2180.09 is computed.
        # However, when triggering the inverse, 2180.09 + (2180.09 * 0.055) = 2180.09 + 119.90 = 2299.99 is computed.
        # To avoid that, set the price_subtotal at the balance if the difference between them looks like a rounding
        # issue.
        if not force_computation and currency.is_zero(amount_currency - price_subtotal):
            return {}

        taxes = taxes.flatten_taxes_hierarchy()
        if taxes and any(tax.price_include for tax in taxes):
            # Inverse taxes. E.g:
            #
            # Price Unit    | Taxes         | Originator Tax    |Price Subtotal     | Price Total
            # -----------------------------------------------------------------------------------
            # 110           | 10% incl, 5%  |                   | 100               | 115
            # 10            |               | 10% incl          | 10                | 10
            # 5             |               | 5%                | 5                 | 5
            #
            # When setting the balance to -200, the expected result is:
            #
            # Price Unit    | Taxes         | Originator Tax    |Price Subtotal     | Price Total
            # -----------------------------------------------------------------------------------
            # 220           | 10% incl, 5%  |                   | 200               | 230
            # 20            |               | 10% incl          | 20                | 20
            # 10            |               | 5%                | 10                | 10
            force_sign = -1 if move_type in ('out_invoice', 'in_refund', 'out_receipt') else 1
            taxes_res = taxes._origin.with_context(force_sign=force_sign).compute_all(amount_currency, currency=currency, handle_price_include=False)
            for tax_res in taxes_res['taxes']:
                tax = self.env['account.tax'].browse(tax_res['id'])
                if tax.price_include:
                    amount_currency += tax_res['amount']

        discount_factor = 1 - (discount / 100.0)
        if amount_currency and discount_factor:
            # discount != 100%
            vals = {
                'quantity': quantity or 1.0,
                'price_unit': amount_currency / discount_factor / (quantity or 1.0),
            }
        elif amount_currency and not discount_factor:
            # discount == 100%
            vals = {
                'quantity': quantity or 1.0,
                'discount': 0.0,
                'price_unit': amount_currency / (quantity or 1.0),
            }
        elif not discount_factor:
            # balance of line is 0, but discount  == 100% so we display the normal unit_price
            vals = {}
        else:
            # balance is 0, so unit price is 0 as well
            vals = {'price_unit': 0.0}
        return vals
    
    @api.model
    def invalidate_cache(self, fnames=None, ids=None):
        print("\n\n pol 55:")
        # Invalidate cache of related moves
        if fnames is None or 'move_id' in fnames:
            field = self._fields['move_id']
            lines = self.env.cache.get_records(self, field) if ids is None else self.browse(ids)
            move_ids = {id_ for id_ in self.env.cache.get_values(lines, field) if id_}
            if move_ids:
                self.env['purchase.order'].invalidate_cache(ids=move_ids)
        return super().invalidate_cache(fnames=fnames, ids=ids)

    @api.depends('debit', 'credit')
    def _compute_balance(self):
        print("\n\n pol 32:")
        for line in self:
            line.balance = line.debit - line.credit
    
    @api.depends('debit', 'credit', 'amount_currency', 'account_id', 'currency_id', 'move_id.state', 'company_id',
                 'matched_debit_ids', 'matched_credit_ids')
    def _compute_amount_residual(self):
        print("\n\n pol 36:")
        """ Computes the residual amount of a move line from a reconcilable account in the company currency and the line's currency.
            This amount will be 0 for fully reconciled lines or lines from a non-reconcilable account, the original line amount
            for unreconciled lines, and something in-between for partially reconciled lines.
        """
        for line in self:
            if line.id and (line.account_id.reconcile or line.account_id.internal_type == 'liquidity'):
                reconciled_balance = sum(line.matched_credit_ids.mapped('amount')) \
                                     - sum(line.matched_debit_ids.mapped('amount'))
                reconciled_amount_currency = sum(line.matched_credit_ids.mapped('debit_amount_currency'))\
                                             - sum(line.matched_debit_ids.mapped('credit_amount_currency'))

                line.amount_residual = line.balance - reconciled_balance

                if line.currency_id:
                    line.amount_residual_currency = line.amount_currency - reconciled_amount_currency
                else:
                    line.amount_residual_currency = 0.0

                line.reconciled = line.company_currency_id.is_zero(line.amount_residual) \
                                  and (not line.currency_id or line.currency_id.is_zero(line.amount_residual_currency))
            else:
                # Must not have any reconciliation since the line is not eligible for that.
                line.amount_residual = 0.0
                line.amount_residual_currency = 0.0
                line.reconciled = False

    def _reconciled_lines(self):
        print("\n\n pol 69:")
        ids = []
        for aml in self.filtered('account_id.reconcile'):
            ids.extend([r.debit_move_id.id for r in aml.matched_debit_ids] if aml.credit > 0 else [r.credit_move_id.id for r in aml.matched_credit_ids])
            ids.append(aml.id)
        return ids

    @api.depends('product_id', 'account_id', 'partner_id', 'date')
    def _compute_analytic_account_id(self):
        print("\n\n pol 9:")
        for record in self:
            if not record.exclude_from_invoice_tab or not record.move_id.is_invoice(include_receipts=True):
                rec = self.env['account.analytic.default'].account_get(
                    product_id=record.product_id.id,
                    partner_id=record.partner_id.commercial_partner_id.id or record.move_id.partner_id.commercial_partner_id.id,
                    account_id=record.account_id.id,
                    user_id=record.env.uid,
                    date=record.date,
                    company_id=record.move_id.company_id.id
                )
                if rec:
                    record.analytic_account_id = rec.analytic_id

    @api.depends('product_id', 'account_id', 'partner_id', 'date')
    def _compute_analytic_tag_ids(self):
        print("\n\n pol 10:")
        for record in self:
            if not record.exclude_from_invoice_tab or not record.move_id.is_invoice(include_receipts=True):
                rec = self.env['account.analytic.default'].account_get(
                    product_id=record.product_id.id,
                    partner_id=record.partner_id.commercial_partner_id.id or record.move_id.partner_id.commercial_partner_id.id,
                    account_id=record.account_id.id,
                    user_id=record.env.uid,
                    date=record.date,
                    company_id=record.move_id.company_id.id
                )
                if rec:
                    record.analytic_tag_ids = rec.analytic_tag_ids