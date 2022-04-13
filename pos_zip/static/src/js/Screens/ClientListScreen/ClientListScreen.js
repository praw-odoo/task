odoo.define("pos_customer.onclickpop", function (require) {
  "use strict";
  const ProductScreen = require("point_of_sale.ProductScreen");
  const Registries = require("point_of_sale.Registries");
  const NewProductScreen = (ProductScreen) =>
    class extends ProductScreen {
      async _onClickPay() {
        var currentClient = this.currentOrder.get_client();
        var self = this;
        if (currentClient) {
          console.log(currentClient.zip);
          if (currentClient.zip == "") {
            const { confirmed, payload } = await this.showPopup(
              "TextInputPopup",
              {
                title: this.env._t("client zip not defined"),
                body: this.env._t("enter client zip"),
              }
            );
            if (confirmed) {
              console.log(payload, "payload");
              currentClient.zip = await this.rpc({
                model: "res.partner",
                method: "write",
                args: [[currentClient.id], { zip: payload }],
                context: this.env.session.user_context,
              }).then(function (e) {
                // self.env.pos.load_new_partners();
                // self.currentOrder.get_client();
                await this.env.pos.load_new_partners();
                this.state.selectedClient = this.env.pos.db.get_partner_by_id(partnerId);
                this.state.detailIsShown = false;
                this.render();
              });
            }
          } else {
            this.showScreen("PaymentScreen");
          }
        } else {
          const { confirmed, payload } = this.showPopup("ErrorPopup", {
            title: this.env._t("client not selected Popup"),
            body: this.env._t("please select client"),
          });
        }
      }
    };
  Registries.Component.extend(ProductScreen, NewProductScreen);
  return ProductScreen;
});
