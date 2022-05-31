from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
import datetime


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    am_cost = fields.Monetary(
        currency_field='currency_id', compute="_compute_asph_inventory_values", string="A&M Cost")
    retrograde_cost = fields.Monetary(
        string="Retrograde Cost", currency_field='currency_id', compute='_compute_asph_inventory_values')
    lowest_value = fields.Monetary(
        string="Lowest Value", currency_field='currency_id', compute='_compute_asph_inventory_values')
    currency_id = fields.Many2one(
        'res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    @api.depends('in_date')
    def _compute_asph_inventory_values(self):
        """computing the values of the fields `am_cost`, `retrograde_cost` and `lowest_value`
        based on the the date matches with `valuation_date` from the asph.inventory.valuation object
        """
        for quant in self:
            quant.am_cost = quant.lowest_value = quant.retrograde_cost = 0
            if quant.in_date:
                max_date = quant.in_date + relativedelta(day=31)
                self._cr.execute("""
                    SELECT
                        am_cost, retrograde_cost
                    FROM
                        asph_inventory_valuation
                    WHERE
                        company_id = %s AND product_id = %s AND valuation_date <= %s::date AND valuation_date <= %s::date
                    ORDER BY
                        valuation_date DESC
                    LIMIT 1
                    """, (self.env.company.id,
                                 quant.product_id.id, datetime.date.today(), max_date))
                result = self.env.cr.dictfetchall()
                if result:
                    for res in result:
                        quant.am_cost = res['am_cost'] * \
                            quant.inventory_quantity
                        quant.retrograde_cost = res['retrograde_cost'] * \
                            quant.inventory_quantity
                        quant.lowest_value = min(
                            quant.am_cost, quant.retrograde_cost)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """ This override is done in order for the grouped list view to display the values of `am_cost`, `retrograde_cost`
        and `lowest_value` int the quants inside a location. This doesn't work out of the box because these all fields are computed
        fields.
        """
        res = super().read_group(domain, fields, groupby, offset=offset,
                                 limit=limit, orderby=orderby, lazy=lazy)
        for group in res:
            if group.get('__domain'):
                quants = self.search(group['__domain'])
                group['am_cost'] = sum(quant.am_cost for quant in quants)
                group['retrograde_cost'] = sum(
                    quant.retrograde_cost for quant in quants)
                group['lowest_value'] = sum(
                    quant.lowest_value for quant in quants)
        return res
