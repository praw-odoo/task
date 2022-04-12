odoo.define("pos_product_qty.ProductItem", function (require) {
  "use strict";
  const ProductItem = require("point_of_sale.ProductItem");
  const Registries = require("point_of_sale.Registries");
  const models = require("point_of_sale.models");
  const NewProductItem = (ProductItem) =>
    class extends ProductItem {
      constructor() {
        super(...arguments);
      }
      OnSubClick() {
        var self = this;
        var order = this.env.pos.get_order();
        if (order.get_orderlines()) {
          order.get_orderlines().forEach(function (orderline) {
            if (orderline.product.id == self.props.product.id) {
              if (orderline.quantity > 0) {
                orderline.set_quantity(orderline.quantity - 1);
              } else if (orderline.quantity == 0) {
                orderline.remove_orderline();
              }
            }
          });
        }
      }
    };
  Registries.Component.extend(ProductItem, NewProductItem);
  return ProductItem;
});
