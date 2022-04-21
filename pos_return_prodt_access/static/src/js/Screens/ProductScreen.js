odoo.define("pos_customer.onclickpop", function (require) {
  "use strict";
  const ProductScreen = require('point_of_sale.ProductScreen');
  const Registries = require('point_of_sale.Registries');
  const NewProductScreen = (ProductScreen) =>
  class extends ProductScreen
  { 
    // this.posmodel.config
    // this.posmodel.user
    async _onClickPay()
    {
      var self = this;
      var users = false
      var quantity = false
      for (var i = 0; i < this.env.pos.get_order().get_orderlines().length; i++)
      {
        quantity = this.env.pos.get_order().get_orderlines()[i].quantity
        if (quantity < 0)
          console.log("quantity : ",quantity)
          break;
      }
      var luid = this.env.pos.user.id
      for (var i = 0; i < self.env.pos.config.access_users.length; i++)
      {
        if (luid == self.env.pos.config.access_users[i])
        {
          users = true
          break;
        }
      }
      if (quantity < 0 && self.env.pos.config.is_check == true && !users)
      {
        const { confirmed, payload } = await this.showPopup("TextInputPopup",
          {
            title: this.env._t("#Access Code Required"),
            body: this.env._t("Please Enter Access Code of user"),
          }
        );
        if (confirmed)
        {
          console.log(payload, "payload");
          var rpc = require('web.rpc');
          rpc.query({
            model: 'res.users',
            method: 'search',
            args: [['&', ['access_code', '=', payload], ['id', 'not in', self.env.pos.config.access_users]]],
          })
          .then(function (data) {
            if (!data.length)
            {
              const { confirmed, payload } = self.showPopup('ErrorPopup',
              {
                title: self.env._t('#Access Code Error'),
                body: self.env._t('Please Enter Correct Access Code'),
              });
            }
            else
            {
              self.showScreen("PaymentScreen");
            }
          })
        }
      }
      else if (quantity < 0 && self.env.pos.config.is_check == true && users)
      {
        self.showScreen("PaymentScreen");
      }
      else
      self.showScreen("PaymentScreen");
    }
  }
  Registries.Component.extend(ProductScreen, NewProductScreen);
  return ProductScreen;
});