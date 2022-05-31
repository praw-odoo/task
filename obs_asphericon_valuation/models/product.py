import datetime
from odoo import fields, models, _
from dateutil.relativedelta import relativedelta


class ProductProduct(models.Model):
    _inherit = 'product.product'

    am_cost = fields.Monetary(
        currency_field='currency_id', compute="_compute_asph_inventory_values", string="A&M Cost")
    retrograde_cost = fields.Monetary(
        string="Retrograde Cost", currency_field='currency_id', compute='_compute_asph_inventory_values')
    lowest_value = fields.Monetary(
        string="Lowest Value", currency_field='currency_id', compute='_compute_asph_inventory_values')
    currency_id = fields.Many2one(
        'res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    asph_inventory_valuation_item_count = fields.Integer(
        compute="_compute_asph_inventory_count")

    def _compute_asph_inventory_count(self):
        for product in self:
            product.asph_inventory_valuation_item_count = 0
            product.asph_inventory_valuation_item_count = self.env["asph.inventory.valuation"].search_count([
                ('product_id', '=', product.id)])

    def _compute_asph_inventory_values(self):
        """computing the values of the fields `am_cost`, `retrograde_cost` and `lowest_value`
        based on the the date matches with `valuation_date` from the asph.inventory.valuation object
        """
        for product in self:
            product.am_cost = product.lowest_value = product.retrograde_cost = 0
            if self.env.context.get('to_date'):
                to_date = self.env.context.get('to_date')
                # converting to_date string object to datetime object
                to_date = datetime.datetime.strptime(
                    to_date, '%Y-%m-%d %H:%M:%S')
                # getting the last date of that particualr month based on to_date
                max_date = to_date + relativedelta(day=31)
                self._cr.execute("""
                SELECT
                    am_cost, retrograde_cost
                FROM
                    asph_inventory_valuation
                WHERE
                    product_id = %s AND valuation_date <= %s::date AND company_id = %s AND valuation_date <= %s::date
                    ORDER BY valuation_date DESC
                LIMIT 1""", (product.id, to_date, self.env.company.id, max_date))
                result = self.env.cr.dictfetchall()
                if result:
                    for res in result:
                        product.am_cost = res['am_cost'] * \
                            product.qty_available
                        product.retrograde_cost = res['retrograde_cost'] * \
                            product.qty_available
                        product.lowest_value = min(
                            product.am_cost, product.retrograde_cost)
    def action_open_asph_entry(self):
        return {
            'name': _('ASPH Inventory Valuation'),
            'type': 'ir.actions.act_window',
            'res_model': 'asph.inventory.valuation',
            'view_mode': 'tree,form',
            'views': [[False, "tree"], [False, "form"]],
            'domain': [['product_id', '=', self.id]],
            'target': 'main'
        }

class ProductTemplate(models.Model):
    _inherit = "product.template"

    asph_inventory_valuation_item_count = fields.Integer(
        compute="_compute_asph_inventory_count")

    def _compute_asph_inventory_count(self):
        for product in self:
            product.asph_inventory_valuation_item_count = 0
            product.asph_inventory_valuation_item_count = self.env["asph.inventory.valuation"].search_count([
                ('product_id', '=', product.product_variant_id.id)])

    def action_open_asph_entry(self):
        return {
            'name': _('ASPH Inventory Valuation'),
            'type': 'ir.actions.act_window',
            'res_model': 'asph.inventory.valuation',
            'view_mode': 'tree,form',
            'views': [[False, "tree"], [False, "form"]],
            'domain': [['product_id', '=', self.product_variant_id.id]],
            'target': 'main'
        }