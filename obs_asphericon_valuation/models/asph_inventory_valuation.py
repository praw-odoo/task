# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AsphInventoryValuation(models.Model):
    _name = 'asph.inventory.valuation'
    _description = "ASPH Inventory Valuation"
    _rec_name = 'product_id'

    _sql_constraints = [
        ("product_unique_valuation_date",
         "UNIQUE(product_id, valuation_date, company_id)",
         "There's already a record for this product at this date."),
    ]

    product_id = fields.Many2one(
        'product.product', string="Product", index=True)
    product_name = fields.Char(string='Product Name', related="product_id.name")
    product_default_code = fields.Char(string='Internal Reference', related="product_id.default_code", store=True)
    valuation_date = fields.Date(string="Valuation Date", index=True, default=fields.Date.today())
    am_cost = fields.Monetary(string="A&M Cost", currency_field='currency_id')
    retrograde_cost = fields.Monetary(
        string="Retrograde Cost", currency_field='currency_id')
    lowest_value = fields.Monetary(
        string="Lowest Value", currency_field='currency_id', compute='_compute_lowest_value')
    currency_id = fields.Many2one(
        'res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company)

    @api.depends('am_cost', 'retrograde_cost')
    @api.onchange('am_cost', 'retrograde_cost')
    def _compute_lowest_value(self):
        """computing the value of field `lowest_value`,
        whichever is lowest from the `am_cost` and `retrograde_cost`
        """
        for inventory in self:
            inventory.lowest_value = min(
                inventory.am_cost, inventory.retrograde_cost)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """ to prevent the `am_cost` and `retrograde_cost` to display values in the group by
        """
        result = super().read_group(domain, fields, groupby, offset=offset,
                                    limit=limit, orderby=orderby, lazy=lazy)
        for res in result:
            if 'retrograde_cost' in res:
                res.pop('retrograde_cost')
            if 'am_cost' in res:
                res.pop('am_cost')
        return result

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        if self._context.get('latest_valution'):
            latest_valuation_dict ={}
            asph_inventory_valuation_ids = self.search([], order="valuation_date DESC")
            for asph_record in asph_inventory_valuation_ids:
                if asph_record.product_id not in latest_valuation_dict:
                    latest_valuation_dict[asph_record.product_id] = asph_record.id
            domain+=[('id', 'in',  list(latest_valuation_dict.values()))]
        return super().search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)
