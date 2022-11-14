odoo.define('jkv_theme.website_form_js', function (require) {
'use strict';

    $(document).ready(function () {
        $("#login, #password").keydown(function(event) {
            if(event.keyCode==13){
                $('#btn_submit_login').click();
            }
        });

        var $oe_login_form = $('.oe_login_form');
        if ($oe_login_form.length > 0) {
            $('.toggle_invisible_password').click(function () {
                if ($('.toggle_invisible_password .show_icon').css('display') === 'none') {
                    $('.toggle_invisible_password .show_icon').css('display', 'block');
                    $('.toggle_invisible_password .hide_icon').css('display', 'none');

                    $(this).parent().find('input').attr('type', 'password');
                } else {
                    $('.toggle_invisible_password .show_icon').css('display', 'none');
                    $('.toggle_invisible_password .hide_icon').css('display', 'block');

                    $(this).parent().find('input').attr('type', 'text');
                }
            });
        }
    });

    var core = require('web.core');
    var ajax = require('web.ajax');
    var snippet_animation = require('web_editor.snippets.animation');

    var qweb = core.qweb;

    // load qweb template
    ajax.loadXML('/jkv_theme/static/src/xml/subscription.xml', qweb);

    var typingTimer;                //timer identifier
    var doneTypingInterval = 1000;  //time in ms, 5 second for example
    var $input = $('#search_all_show_name_input');
    var $input2 = $('#search_my_show_name_input');

    //on keyup, start the countdown
    $input.on('keyup', function () {
      clearTimeout(typingTimer);
      typingTimer = setTimeout(doneTyping($input.val()), doneTypingInterval);
    });

    $input2.on('keyup', function () {
      clearTimeout(typingTimer);
      typingTimer = setTimeout(doneTyping($input2.val()), doneTypingInterval);
    });

    //on keydown, clear the countdown
    $input.on('keydown', function () {
      clearTimeout(typingTimer);
    });

    $input2.on('keyup', function () {
      clearTimeout(typingTimer);
    });

    //user is "finished typing," do something
    function doneTyping (value) {
          $.ajax({
                type: "POST",
                url: "/filter_shows",
                data: JSON.stringify({
                    jsonrpc: "2.0",
                    method: "call",
                    params: {
                         "filter_string":value,
                         "type_video": $("input[name='type_video']").val(),
                     }
                }),
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function(data){
                    var result = data['result'];
                    if (result.shows.length > 0){
                        if (result.type_video == "all_videos"){
                            $('#purchase_subscription .subscription-list').remove();
                            $("#purchase_subscription").append(qweb.render('jkv_theme.filter_shows', {'shows':result.shows}));
                        }
                        else{
                            $('#purchase_subscription_myvideo .subscription-list').remove();
                            $("#purchase_subscription_myvideo").append(qweb.render('jkv_theme.filter_shows', {'shows':result.shows}));
                        }
                    }
                    else{
                        if (result.type_video == "all_videos"){
                            $('#purchase_subscription .subscription-list').remove();
                        }
                        else{
                            $('#purchase_subscription_myvideo .subscription-list').remove();
                        }
                    }
                }
            });
    }

    snippet_animation.registry.form_builder_send.include({
        send: function(e) {
            e.preventDefault();  // Prevent the default submit behavior
            this.$target.find('.o_website_form_send').off().addClass('disabled');  // Prevent users from crazy clicking

            var self = this;

            self.$target.find('#o_website_form_result').empty();
            if (!self.check_error_fields([])) {
                self.update_status('invalid');
                return false;
            }

            // Prepare form inputs
            this.form_fields = this.$target.serializeArray();
            _.each(this.$target.find('input[type=file]'), function(input) {
                $.each($(input).prop('files'), function(index, file) {
                    // Index field name as ajax won't accept arrays of files
                    // when aggregating multiple files into a single field value
                    self.form_fields.push({
                        name: input.name + '[' + index + ']',
                        value: file
                    });
                });
            });

            // Serialize form inputs into a single object
            // Aggregate multiple values into arrays
            var form_values = {};
            _.each(this.form_fields, function(input) {
                if (input.name in form_values) {
                    // If a value already exists for this field,
                    // we are facing a x2many field, so we store
                    // the values in an array.
                    if (Array.isArray(form_values[input.name])) {
                        form_values[input.name].push(input.value);
                    } else {
                        form_values[input.name] = [form_values[input.name], input.value];
                    }
                } else {
                    if (input.value != '') {
                        // Check if submit contact form, then convert datetime picker to format en-us
                        if (self.$target.context.id === "jkv_form_contact"){
//                            if (input.name == 'event_date'){
//                                form_values[input.name] = new Date(input.value).toLocaleDateString("en-US");
//                            }
                              if(input.name == 'is_rider' || input.name == 'is_trainer'
                              || input.name == 'is_owner' || input.name == 'is_event_producer_manager' ){
                                 form_values[input.name] = true;
                              }
                              else{
                                form_values[input.name] = input.value;
                              }
                        }
                        else{
                            form_values[input.name] = input.value;
                        }
                    }
                }
            });

            // Overwrite form_values array with values from the form tag
            // Necessary to handle field values generated server-side, since
            // using t-att- inside a snippet makes it non-editable !
            for (var key in this.$target.data()) {
                if (_.str.startsWith(key, 'form_field_')){
                    form_values[key.replace('form_field_', '')] = this.$target.data(key);
                }
            }

            // Check if submit login form or signup form, then submit form
            if (self.$target.context.id === "jkv_form_login" || self.$target.context.id === "jkv_form_signup" || self.$target.context.id === "jkv_form_reset_password") {
                if (self.$target.context.id === "jkv_form_signup") {
                    var recaptcha = $("#g-recaptcha-response").val();
                    if (recaptcha === "") {
                        self.update_status('error');
                        alert('Please check the recaptcha');
                    } else {
                        document.getElementById(self.$target.context.id).submit();
                    }
                } else {
                    document.getElementById(self.$target.context.id).submit();
                }
            }
            else{
                $( "div.se-pre-con" ).fadeIn( "slow" );
                // Post form and handle result
                ajax.post(this.$target.attr('action') + (this.$target.data('force_action')||this.$target.data('model_name')), form_values)
                    .then(function(result_data) {
                    result_data = $.parseJSON(result_data);
                    if(!result_data.id) {
                        $( "div.se-pre-con" )[0].style.display = "none"
                        // Failure, the server didn't return the created record ID
                        self.update_status('error');
                        if (result_data.error_fields && result_data.error_fields.length) {
                            // If the server return a list of bad fields, show these fields for users
                            self.check_error_fields(result_data.error_fields);
                        }
                    } else {
                        // Success, redirect or update status
                        var success_page = self.$target.attr('data-success_page');
                        if(success_page) {
//                            $(location).attr('href', success_page);
                                $(location).attr('href', "/page/thank");
                        }
                        else {
                            $( "div.se-pre-con" )[0].style.display = "none"
                            self.update_status('success');
                        }

                        // Reset the form
                        self.$target[0].reset();
                    }
                })
                .fail(function(result_data){
                    self.update_status('error');
                });
            }
        },

        update_status: function(status) {
            var self = this;
            if (status != 'success') {  // Restore send button behavior if result is an error
                this.$target.find('.o_website_form_send').on('click',function(e) {self.send(e);}).removeClass('disabled');
            }
        },
    });
});
