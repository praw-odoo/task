odoo.define("pos_slip_number.models", function (require) {
    "use strict";
    console.log("hello world")
    const Registries = require("point_of_sale.Registries");
    const models = require("point_of_sale.models");
    const Newmodels = (models) =>
        class extends models {
            constructor() {
                super(...arguments);
            }

            export_for_printing (){
                return {
                    sequence_num: this.name
                   
                };
            }
            // export_for_printing() {
            //     console.log("hello world")
            //     return {
            //         sequence_num = '1'
            //     }
                // var _super_order = models.Order.prototype;
                // var result = _super_order.export_for_printing.apply(this, arguments);
                // // sequence_num = pos_order.sequence_num
                // var sequence_num  = new Model('pos_order').call('create').then(function(result){
                //     return result;
                // });
                // result.sequence_num
                // return {
                //     result
                // }
                //     sequence_num = await this.rpc({
                //         model: "pos.order",
                //         method: "read",
                //         args: [id],
                //         context: this.env.session,
                //       })
                // };
            // };
             
      };
    Registries.Component.extend(models, Newmodels);
    return models;
  });
  