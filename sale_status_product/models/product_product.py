from odoo import api, models, fields
from odoo.osv import expression
from odoo import SUPERUSER_ID


class ProductProduct(models.Model):
    _inherit = "product.product"

    # method 1
    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        '''
        ths method helps to display product suggestion from given domain 
        '''
        print("\n\n self.env.context : ",self.env.context)
        filtered_status = self.env['sale.order'].search([('partner_id','=',self.env.context.get('partner_id')),('state','=','sale')]).mapped("order_line.product_id").ids
        if self.env.context.get('partner_id'):
            domain = expression.AND([args or [], [('id', 'in', filtered_status)]])
            return super()._name_search(name=name, args=domain, operator=operator, limit=limit, name_get_uid=SUPERUSER_ID)
        return super()._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)

    # method 2
    # @api.onchange('product_id')
    # def _onchange_product_id(self):
        
    #     filtered_status = self.search([('order_id.partner_id','=',self.order_id.partner_id.id) ]).mapped("product_id").ids
    #     print("\n\n filtered_status :",filtered_status)
    #     return {
    #         'domain': {
    #             'product_id': [
    #                 ('id', 'in', filtered_status)
    #             ]}
    #     }

    # @api.model
    # def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
    #     filtered_status = self.env["sale.order"].search([('partner_id','=',self.env.context.get('partner_id')),('state','=','sale')]).mapped("order_line.product_id").ids
    #     print("\n\n filtered_status :",filtered_status)
    #     if filtered_status:
    #         domain = expression.AND([args or [], [('id', 'in', filtered_status)]])
    #         return super()._name_search(name=name, args=domain, operator=operator, limit=limit, name_get_uid=SUPERUSER_ID)
    #     return super()._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)        
