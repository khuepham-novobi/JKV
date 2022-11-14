odoo.define('jkv_theme.jkv_livestream_videos', function (require) {
    "use strict";
    $(document).ready(function () {
        function getUrlParams(url) {
            var params = {};
            url.substring(1).replace(/[?&]+([^=&]+)=([^&]*)/gi,
                    function (str, key, value) {
                         params[key] = value;
                    });
            return params;
        }
        var href = window.location.href;
        var location = document.location;
        var params = getUrlParams(href);
        var is_livestream_video = params['is_livestream_product'] || false;
         if(is_livestream_video && location.pathname == '/shop'){
            var $dropdown_menu = $(".main-nav li.dropdown:contains('videos') a").next('.dropdown-menu');
            $dropdown_menu.find('li').siblings().removeClass('active');
            $dropdown_menu.find('li a[href="/shop/?is_livestream_product=true"]').parent('li').addClass('active');
         }
        var is_livestream_subscription = params['is_livestream_subscription'] || false;
        if(is_livestream_subscription && location.pathname == '/purchase_subscription'){
           var psl = $("#purchase_subscription_livestream .show_name_subscription");
           if(psl.length > 0 && !psl.hasClass('selected')){
               psl.click();
           }
        }
    });
});