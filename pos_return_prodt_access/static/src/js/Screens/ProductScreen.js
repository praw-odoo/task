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
      console.log(self.env.pos.config.is_check)
      console.log("self.env.pos.config.access_users : ",self.env.pos.config.access_users)
      if (self.env.pos.config.is_check == true && self.env.pos.config.access_users != null)
      {
        console.log("this", this)
        console.log("self",self)
        const { confirmed, payload } = await this.showPopup("TextInputPopup",
          {
            title: this.env._t("#Access Code Required"),
            body: this.env._t("Please Enter Access Code of user"),
          }
        );
        if (confirmed)
        {
          console.log(self.env.pos.user)
          console.log(payload, "payload");
          var rpc = require('web.rpc');
          rpc.query({
            model: 'res.users',
            method: 'search',
            args: [['&', ['access_code', '=', payload], ['id', '=', self.env.pos.user.id]]],
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
    }
  }
  Registries.Component.extend(ProductScreen, NewProductScreen);
  return ProductScreen;
});