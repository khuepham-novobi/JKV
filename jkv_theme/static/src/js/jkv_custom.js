odoo.define('jkv_theme.custom_js',['jkv_product.multi_video'], function (require) {
    "use strict";

    $(document).ready(function () {
        $("#searchBtn").click(function() {
        $("#searchBar").fadeIn(100,);
            $("#closeBtn").click(function() {
                $(".search-nav").fadeOut(100);
            });
        });
        $('#defaultNavbar1').on('show.bs.collapse', function () {
          $('header').addClass('m-menu');
        });

        $('#defaultNavbar1').on('hide.bs.collapse', function () {
          $('header').removeClass('m-menu');
        });

         $("#collapseResp ul li").click(function(){
            $(this).find("input").click();
        });

        $('.oe_cart').on('click', '.js_delete_product', function(e) {
            e.preventDefault();
            $(this).parents('div.flex-col').find('input.js_quantity').val(0).trigger('change');
        });

        function check_date(){
            if ($('#jkv_start_date_search_result_video').val() != '' && $('#jkv_end_date_search_result_video').val() != ''){
                if ($('#jkv_start_date_search_result_video').val() > $('#jkv_end_date_search_result_video').val()) {
                    $('#jkv_date_search_warning').modal('toggle');
                }
                else {
                    $( "div.se-pre-con" ).fadeIn( "slow" );
                    $('#form-panel-search-result').submit();
                }
            }
            else{
                $( "div.se-pre-con" ).fadeIn( "slow" );
                $('#form-panel-search-result').submit();
            }
        }

        function format_phoneUS(phoneNumber){
           var format ="(";
           phoneNumber = phoneNumber.replace(/\D/g, '');
           if (phoneNumber.length == 0){
               return ''
           }
           else if (phoneNumber.length > 10){
                phoneNumber = phoneNumber.slice(0,10);
           }
           for (var i=0;i<phoneNumber.length;i++){
                if (i < 3){
                    format = format + phoneNumber[i];
                }
                else if (i==3){
                    format = format + ") "+phoneNumber[i];
                }
                else if ((i>3) && (i<6)){
                    format = format + phoneNumber[i];
                }
                else if (i==6){
                    format = format + "-" + phoneNumber[i];
                }
                else{
                    format = format + phoneNumber[i]
                }
           }
           return format;
        }

        function formatGenericPhone(phoneNumber) {
            phoneNumber = phoneNumber.replace(/\D/g, '');
            phoneNumber = phoneNumber.slice(0, 15);
            return phoneNumber;
        }

        $('.show_name_search_result2').on('change', function (event) {
            check_date();
        });

        $('li.blog_article_search_result').click(function (e) {
            var cb = $(this).find(":checkbox")[0];
            if (e.target != cb) cb.checked = !cb.checked;
            $(this).toggleClass("checked", cb.checked);
            $( "div.se-pre-con" ).fadeIn( "slow" );
            $('#form-panel-search-result').submit();
        });

         $(".changeArticle").click(function(event) {
            $( "div.se-pre-con" ).fadeIn( "slow" );
        });

        $('.js_edit_address').click(function() {
            $(this).parent('div.box-tit').find('form').attr('action', '/shop/address').submit();
        });

        $('#purchase_subscription_form').on('click', '#video', function (event) {
            $("input[name='type_video']").val('my_video');
            $("#purchase_subscription li.show_name_subscription").each(function(e){
                 $(this).removeClass("selected");
                 $(this).children('input').prop('checked', false);
            });
        });

        $('#purchase_subscription_form').on('click', '#show', function (event) {
            $("input[name='type_video']").val('all_videos');
            $("#purchase_subscription_myvideo li.show_name_subscription").each(function(e){
                 $(this).removeClass("selected");
                 $(this).children('input').prop('checked', false);
            });
        });

        $('#purchase_subscription').on('click', 'li.show_name_subscription', function (event) {
            if ($(this).hasClass('selected')) {
                $(this).removeClass("selected");
                $(this).children('input').prop('checked', false);
            } else {
                $(this).addClass("selected");
                $(this).children('input').prop('checked', true);
            }
        });

        $('#purchase_subscription_livestream').on('click', 'li.show_name_subscription', function (event) {
            if ($(this).hasClass('selected')) {
                $(this).removeClass("selected");
                $(this).children('input').prop('checked', false);
            } else {
                $(this).addClass("selected");
                $(this).children('input').prop('checked', true);
            }
        });

        $('#purchase_subscription_myvideo').on('click', 'li.show_name_subscription', function (event) {
            if ($(this).hasClass('selected')) {
                $(this).removeClass("selected");
                $(this).children('input').prop('checked', false);
            } else {
                $(this).addClass("selected");
                $(this).children('input').prop('checked', true);
            }
        });

        $("#confirm_purchase_payment").click(function(){
            if(!$(this).find('i.fa').length){
                $(this).append('<i class="fa fa-spinner fa-spin"/>');
                $(this).attr('disabled','disabled');
            }
            $("#pay_stripe").trigger("click");
            var interval = setInterval(function(){
                if (!$("#pay_stripe").find('i').length){
                    $("#confirm_purchase_payment").removeAttr('disabled').find('i.fa').remove();
                    clearInterval(interval);
                }
            }, 500);
        });

        setTimeout(function(){
            if (window.location.pathname=="/shop/confirmation"){
//                window.location.href = '/my/home';
                var home_url = '/my/home';
                var is_redirect = $("input[name='is_redirect']").val()
                if (is_redirect){
                    var redirect_url = $("input[name='redirect_url']").val()
                    if (redirect_url){
                       window.location.href = redirect_url;
                    }
                    else{
                        window.location.href = home_url;
                    }
                }else{
                    window.location.href = home_url;
                }
            }
        },5000);

        $(".renew_button").click(function(){
            var subscription_id = $(this).attr("data-id");
            $("#renew_subscription_id").val(subscription_id);
            $("#submit_form_renew").trigger("click");
        });

         $(".renew_livestream_button").click(function(){
             var subscription_id = $(this).attr("data-id");
            $("#renew_livestream_subscription_id").val(subscription_id);
            $("#submit_form_renew_livestream").trigger("click");
        });

        $(".confirm_purchase_subscription").click(function(){
            $("#submit_purchase_subcription").val(true);
            $("#submit_form").trigger("click");
        });

        var state_options = $("select[name='state_id']:enabled option:not(:first)");
        $('#jkv_form_signup').on('change', "select[name='country_id']", function () {
            var select = $("select[name='state_id']");
            state_options.detach();
            var displayed_state = state_options.filter("[data-country_id=" + ($(this).val() || 0) + "]");
            var nb = displayed_state.appendTo(select).show().size();
            select.parent().toggle(nb >= 1);
        });
        $('#jkv_form_signup').find("select[name='country_id']").change();

        var $countrySelect = $("select[name='country_id']");
        $("#phone").keyup(function() {
            var format = $(this).val();
            var $selectedCountry = $countrySelect.find("option:selected");
            var isUS = _.str.strip($selectedCountry.data('code')) === 'US';
            format = isUS ? format_phoneUS(format) : formatGenericPhone(format);
            $(this).val(format);
        });

        $('#button_submit_confirm_change_user_details').unbind("click").click(function(event) {
            $('#confirm_change_user_details').modal('toggle');
        });

        $('#button_confirm_change_user_details').unbind("click").click(function(event) {
            $("input[name='name']").val($("input[name='jkv_first_name']").val() + " " + $("input[name='jkv_last_name']").val());
            $('#form_change_user_detailts').submit();
        });

        $('.purchased_video_thumb').click(function(event){
            var video_link = $(this).parent().find('a.purchased-video-info');
            video_link[0].click();
        });

        var slideIndex = 0;
        var timOut;
        showSlides();

        function showSlides() {
            var i;
            var slides = document.getElementsByClassName("IndividualSlideShow");
            var slidesButton = document.getElementsByClassName("IndividualSlidesCalendarButton");
            if(slides.length >= 1 && slidesButton.length >= 1 ) {
                for (i = 0; i < slides.length; i++) {
                    slides[i].style.display = "none";
                    slidesButton[i].style.display = "none";
                }
                if (slideIndex > slides.length - 1) {
                    slideIndex = 0
                }
                slides[slideIndex].style.display = "block";
                slidesButton[slideIndex].style.display = "block";
                slideIndex++;
                if(typeof timOut !== "undefined") {
                    clearTimeout(timOut);
                }
                timOut = setTimeout(showSlides, 10000); // Change image every 5 seconds
            }
        }

        $('.o_prev_slides').click(function() {
            if(slideIndex > 1)
            {
                slideIndex = slideIndex - 2;
                showSlides();
            } else {
                if (slideIndex == 1)
                {
                    var slides = document.getElementsByClassName("IndividualSlideShow");
                    slideIndex = slides.length - 1;
                    showSlides();
                }
            }
        });

        $('.o_next_slides').click(function() {
            var slides = document.getElementsByClassName("IndividualSlideShow");
            if(slideIndex == slides.length)
            {
                slideIndex = 0;
            }
            showSlides();
        });

         var temp = 1;
         $('#mainMenu').click(function() {
         if(temp == 1){
            document.getElementById('oe_main_menu_navbar').style.display = 'none';
            document.getElementsByClassName('o_connected_user')[0].style.cssText= 'padding-top:0px !important';
            temp = 0;
         } else {
            document.getElementById('oe_main_menu_navbar').style.display = '';
            document.getElementsByClassName('o_connected_user')[0].style.cssText= 'padding-top:46px !important';
            temp = 1;
         }
        });

        $('.loginOverlay').click(function (e) {
            document.getElementById("login-overlay").style.display = "";
            setTimeout(function() {
              document.getElementById("login-overlay").style.display = "none";
              $(location).attr('href', "/web/login");
            }, 4000);
        });
    });
});

