odoo.define('jkv_website_purchase.purchase', function(require) {
    var core = require('web.core');
    var ajax = require('web.ajax');
    var QWeb = core.qweb;
	$(document).ready(function () {

        $(".radio_duration").change(function() {
            /*
            var all_videos = $("#all_videos:checked").length > 0;
            if (all_videos){
                $.ajax({
                    type: "POST",
                    url: "/get_shows",
                    // The key needs to match your method's input parameter (case-sensitive).
                    data: JSON.stringify({
                        jsonrpc: "2.0",
                        method: "call",
                        params: {
                         "all_videos":true}
                    }),
                    contentType: "application/json; charset=utf-8",
                    dataType: "json",
                    success: function(data){
                        var result = data['result'];
                        if (result){
                            $("#table_shows_purchase_subscription").remove();
                            $("#shows_for_purchase_subscription").append(QWeb.render('jkv_website_purchase.shows_purchase_subscription_page',{'shows':result}))                            
                        }
                    }   
                });
            }
            else{
                $("#div_shows_uid").css('display','block');
                $("#div_shows").css('display','none');
            }*/
            $("#submit_form").trigger("click");
        })

        var token = $("#purchase_token").val();
        // Deprecated from_ios_page -> Just let the user try to download the video
        // var from_ios_page = $("#from_ios_page").val();
        // Download page (Thank you page)
        if (token) {
            ajax.jsonRpc("/download", 'call', {token: token})
                .then(function(result) {
                    if (result && !result.success) {
                        $('.fa.fa-spinner').parent().css('visibility', 'hidden');
                        $('#download_msg').text('Download failed. Please try again or contact JK for help.');
                        $('#download_back').show();
                    }
                    else if (result && result.success) {
                        var link = document.createElement('a');
                        link.href = result['url'];
                        link.download = result['video_name'];
                        link.click();
                        // Wait for download dialog to pop up and give user time to choose
                        setTimeout(function () {
                            window.location = "/my/home";
                        }, 15000);
                    }
                });
        }
        
        $(".renew_button").click(function(){
            var subscription_id = $(this).attr("data-id");
            $("#renew_subscription_id").val(subscription_id);
            $("#submit_form_renew").trigger("click");
            //$('#renewModal').modal({backdrop: 'static', keyboard: false});
            //$('#renewModal').modal('show');
        });
        
        $("#confirm_purchase_subscription").click(function(){
            
            $("#submit_purchase_subcription").val(true);
            $("#submit_form").trigger( "click" );
        });
        
        $("#purchase_video_button").click(function(){
            var product_id = $("#purchase_product_id").val();
            $.ajax({
                type: "POST",
                url: "/purchase_video",
                // The key needs to match your method's input parameter (case-sensitive).
                data: JSON.stringify({
                    jsonrpc: "2.0",
                    method: "call",
                    params: {
                     "product_id":product_id}
                 }),
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function(data){
                    var code = data['result']['code'];
                    if (code == 200){
                        window.location.href = "/sent_email";
                    }

                }
                
            });
        });
    });

});
