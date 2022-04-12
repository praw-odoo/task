odoo.define("pos_customer.onclickpop", function (require) {
    "use strict";
    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');
    const NewProductScreen = (ProductScreen) =>
        class extends ProductScreen {
            _onClickPay()
            {
                const currentClient = this.currentOrder.get_client();
                if (currentClient)
                {
                    this.showScreen('PaymentScreen');
                }
                else
                {
                    const { confirmed, payload } = this.showPopup('ErrorPopup', {
                        title: this.env._t('client not selected Popup'),
                        body: this.env._t('please select client'),
                    });
                }
            }
        }
        Registries.Component.extend(ProductScreen, NewProductScreen);
        return ProductScreen;
});