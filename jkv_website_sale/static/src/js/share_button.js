odoo.define('jkv_website_sale.share_button', function(require) {
    "use strict";

    var Widget = require('web.Widget');

    var ShareModalWiget = Widget.extend({
        events: {
            'click .copy_btn': 'onClickCopy'
        },
        start: function() {
            var self = this;
            this.$el.on('hidden.bs.modal', function() {
                self.$el.find('.notification_div').text('');
            });
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

    var ShareButtonWidget = Widget.extend({
        events: {
            'click i': 'onClickShare'
        },
        init: function(parent, $shareModal) {
            this._super(parent);
            this.parent = parent;
            this.$shareModal = $shareModal;
        },
        onClickShare: function(ev) {
            var link = $(ev.currentTarget).data('link').toString();
            this.$shareModal.find('#share_link_input').val(link);
            this.$shareModal.modal('show');
        }
    });

    $(document).ready(function() {
        var $shareModal = $('#share_modal');
        var shareModalWiget = new ShareModalWiget();
        shareModalWiget.attachTo($shareModal);
        $('.share_button').each(function() {
            var shareWidget = new ShareButtonWidget(null, $shareModal);
            shareWidget.attachTo($(this));
        });
    });

    return {
        'share_modal_widget': ShareModalWiget,
        'share_button_widget': ShareButtonWidget
    };
});