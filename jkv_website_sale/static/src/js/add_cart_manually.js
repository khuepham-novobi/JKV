odoo.define('jkv_website_sale.add_cart_manually', function(require) {
    "use strict";

    var ajax = require('web.ajax');
    var signedIn = false;
    ajax.jsonRpc("/shop/uid", 'call', {}).then(function(result) {
        if(result && result.uid) {
            signedIn = true;
        }
    });

    var Widget = require('web.Widget');

    var AddCartManually = Widget.extend({
        init: function(parent, $furnito_theme_cart_quantity, $video_form_notification) {
            this._super(parent);
            this.parent = parent;
            this.$furnito_theme_cart_quantity = $furnito_theme_cart_quantity;
            this.$video_form_notification = $video_form_notification;
        },
        start: function() {
            this.assignEvents();
        },
        assignEvents: function() {
            var self = this;
            this.$el.submit(function(e) {
                e.preventDefault();
                if(!signedIn) {
                    var productId = parseInt($(e.currentTarget).find('input[name=product_id]').val());
                    window.location.href = '/web/login' + '?productId=' +  productId;
                    return false;
                }
                var $form = $(e.currentTarget);
                var productId = parseInt($form.find('input[name=product_id]').val());
                var $notification = self.$video_form_notification;
                var $textArea = $notification.find('strong');
                $textArea.empty().text('Processing Request. Please wait...');
                $notification.modal('show');  // hide in post function
                ajax.jsonRpc("/shop/cart/update_json", 'call', {
                    'product_id': productId,
                    'set_qty': 1
                }).then(function (data) {
                    if(data && 'cart_quantity' in data) {
                        var oldText = parseInt(self.$furnito_theme_cart_quantity.first().text());
                        var newQty = parseInt(data['cart_quantity']);
                        self.$furnito_theme_cart_quantity.text(newQty);
                        $notification.find('strong').empty().text(oldText === newQty ? 'This video is already in cart.' : 'Video added to cart.');
                    }
                    setTimeout(function() {
                        $notification.modal('hide');
                    }, 1500);
                });
            });
        }
    });

    $(document).ready(function() {
        var $cart_quantity = $('.furnito_theme_cart_quantity');
        var $notification = $('.video_form_notification');
        $('form.video_form').each(function() {
            var widget = new AddCartManually(null, $cart_quantity, $notification);
            widget.attachTo($(this));
        });
    });

    return AddCartManually;
});