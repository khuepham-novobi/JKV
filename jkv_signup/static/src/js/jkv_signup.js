odoo.define('jkv_signup.signup', function (require) {
"use strict";
    var Model = require('web.Model');
    var ResUsers = new Model("res.users");
    function validateEmail(email) {
        var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(email);
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

    $(document).ready(function () {

        $("#confirm_remove_account").click(function(){
            var password = $("#remove_password").val();            
            $.ajax({
                type: "POST",
                url: "/remove_account",
                // The key needs to match your method's input parameter (case-sensitive).
                data: JSON.stringify({
                    jsonrpc: "2.0",
                     method: "call",
                     params: {
                     "password":password}
                }),
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function(data){
                    var code = data['result']['code'];
                    if (code == 100){
                        $("#error_remove_account").text(data['result']['message']);
                        $("#error_remove_account").css('display','block');
                    }
                    else{
                        window.location.href = "/shop";
                    }
                }
                
            });
        });
        var $signUpForm = $("#jkv_form_signup");
        var $countrySelect = $signUpForm.find("select[name='country_id']");
        $("#phone").keyup(function() {
            var format = $(this).val();
            var $selectedCountry = $countrySelect.find("option:selected");
            var isUS = _.str.strip($selectedCountry.data('code')) === 'US';
            format = isUS ? format_phoneUS(format) : formatGenericPhone(format);
            $(this).val(format);
        });
        
        $("#phone_register").keyup(function() {
            var format = $(this).val();
            var $selectedCountry = $countrySelect.find("option:selected");
            var isUS = _.str.strip($selectedCountry.data('code')) === 'US';
            format = isUS ? format_phoneUS(format) : formatGenericPhone(format);
            $(this).val(format);
        });

        /*For mobile device*/
        $("#city_xs").keyup(function() {
            $("input[name='city']").val($(this).val());
        });
        $("#state_id_xs").change(function() {
            $("select[name='state_id']").val($(this).val());
        });
        $("#zip_code_xs").keyup(function() {
            $("input[name='zip_code']").val($(this).val());
        });

        $("input[name='city']").keyup(function() {
            $("#city_xs").val($(this).val());
        });
        $("select[name='state_id']").change(function() {
            $("#state_id_xs").val($(this).val());
        });
        $("input[name='zip_code']").keyup(function() {
            $("#zip_code_xs").val($(this).val());
        });

        $('#button_submit_confirm_change_user_details').unbind("click").click(function(event) {
            $('#confirm_change_user_details').modal('toggle');
        });

        $('#button_confirm_change_user_details').unbind("click").click(function(event) {
            $('#form_change_user_detailts').submit();
        });
        
    });   
    
});
