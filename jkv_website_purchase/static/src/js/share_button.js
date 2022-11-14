odoo.define('jkv_website_purchase.share_button', function(require) {
    "use strict";

    var Widget = require('web.Widget');

    var ShareButtonWidget = Widget.extend({
        events: {
            'click .share_btn': 'onClickShare',
            'click .copy_btn': 'onClickCopy'
        },
        start: function() {
            var self = this;
            this.$el.find('#share_modal').on('hidden.bs.modal', function() {
                self.$el.find('.notification_div').text('');
            });
        },
        onClickShare: function() {
            this.$el.find('#share_modal').modal('show');
        },
        onClickCopy: function() {
            var linkInput = this.$el.find('#share_link_input').get(0);
            linkInput.select();
            try {
                document.execCommand("copy");
                this.$el.find('.notification_div').text('Copied to clipboard!');
            }
            catch(e) {
                this.$el.find('.notification_div').text(e.message);
            }
        }
    });

    $(document).ready(function() {
        $('.share_link_div').each(function() {
            var shareWidget = new ShareButtonWidget();
            shareWidget.attachTo($(this));
        });
    });

    return ShareButtonWidget;
});