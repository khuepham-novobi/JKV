odoo.define('jkv_product.multi_video', function(require) {
	$(document).ready(function () {
	    
	    //Trigger add to card when clicking purchase video on dialog
        $(".btn_confirm_purchase").click(function(){
            $("#add_to_cart").trigger('click');
        })

        //Change source Video popup
        $(".jkv_sample_video").click(function(){
            var source = $(this).attr("source")
            $("#jkv_sample_video .modal-body video source").attr("src",source);
            $("#jkv_sample_video .modal-body video").load().contextmenu(function(ev) {
                ev.stopPropagation();
                ev.preventDefault();
            });
        });
        $(".jkv_main_video").click(function(){
            var source = $(this).attr("source")
            $("#jkv_main_video .modal-body video source").attr("src",source);
            $("#jkv_main_video .modal-body video").load().contextmenu(function(ev) {
                ev.stopPropagation();
                ev.preventDefault();
            });
        });

		// Close popup Sample Video 
		$( "#jkv-cancel_video_sample_popup").click(function() {
			$("#jkv_sample_video").css("display", "none");
		});
        var show_status = $("#show_status").val();
        if (show_status == "True"){
            $('#statusModal').modal({backdrop: 'static', keyboard: false});
            $('#statusModal').modal('show');
        }
        
        $("#close_status_modal").click(function(){
            var close_checkbox = $('#not_show:checked').length > 0;
            if (close_checkbox == true){
                $.get( "/close_status");
            }
        });
        
        var now = $("#current_date").val();
        var subscription = $("#subscription").val();
        var not_play = $("#not_play").val();
        now = new Date(now);
        $('.product_detail_video').bind('play', function (e) {           
            var end_date = $(this).attr("end-date").split("-");
            end_date = new Date(end_date);
            if (((end_date.getTime() < now.getTime()) && (subscription != '1') && not_play == '1')) {
                this.pause();
                $('#pauseModal').modal('show');
            }            
        }).contextmenu(function (ev) {
            ev.stopPropagation();
            ev.preventDefault();
        });
        $( "#jkv_start_date_search_video" ).datetimepicker({
            pickDate:true,
            pickTime: false});
        $( "#jkv_end_date_search_video" ).datetimepicker({
            pickDate:true,
            pickTime: false});
        $( '#jkv_start_date_search_result_video' ).datetimepicker({
            pickDate:true,
            pickTime: false});
        $( '#jkv_end_date_search_result_video' ).datetimepicker({
            pickDate:true,
            pickTime: false});

        $("#button_search_info").unbind("click").click(function(event) {
            if ($('#jkv_start_date_search_video').val() == '' || $('#jkv_end_date_search_video').val() == ''){
                $('#jkv_date_search_confirm').modal('toggle');
            }
            else if ($('#jkv_start_date_search_video').val() > $('#jkv_end_date_search_video').val()) {
                $('#jkv_date_search_warning').modal('toggle');
            }
            else{
                $('#form_search_info').submit();
            }
        });

        $('#button_search_confirm_date_info').unbind("click").click(function(event) {
            $('#form-panel-search-result').submit();
            $('#form_search_info').submit();
        });

        $('#button_search_result').unbind("click").click(function(event) {
            var check_empty = true;
            $("#form_search_result input:checked").each(function() {
                if($(this).val() != "" && $(this).val() != 'jkv_save_filter'){
                    check_empty = false;
                }
            });
            if (check_empty == false){
                $('#form_search_result').submit();
            }
            else
                $('#jkv_date_search_for_result_confirm').modal('toggle');
        });

        $('#button_search_for_result_confirm_date_info').unbind("click").click(function(event) {
            $('#form_search_result').submit();
        });

        $('#button_view_last_filter').unbind("click").click(function(event) {
            $("#jkv_view_last_filter").val(true);
            $('#form_search_result').submit();
        });

        $("input.subscribed_or_show_all:checkbox").on('click', function() {
            if ($(this).is(":checked")) {
                $('#subscribed_video_only').prop("checked", false);
                $('#show_my_videos').prop("checked", false);
                $('#show_my_videos_hidden').prop("checked", false);
                $('#subscribed_video_only_hidden').prop("checked", false);
                $(this).prop("checked", true);
                if ($(this).attr('id') == 'show_my_videos'){
                    $('#show_my_videos_hidden').prop("checked", true);
                }
                else if ($(this).attr('id') == 'subscribed_video_only'){
                    $('#subscribed_video_only_hidden').prop("checked", true);
                }
            } else {
                $(this).prop("checked", false);
                if ($(this).attr('id') == 'show_my_videos'){
                    $('#show_my_videos_hidden').prop("checked", false);
                }
                else if ($(this).attr('id') == 'subscribed_video_only'){
                    $('#subscribed_video_only_hidden').prop("checked", false);
                }
            }
        });

        function toggleChevron(e) {
            $(e.target)
            .prev('.panel-heading')
            .find('i.icon_accordion')
            .toggleClass('fa-chevron-down fa-chevron-up');
        }
        function setJKVCollapse(e){
            $("#jkv_collapse").val($(e.target).attr("id"));
        }
        $('#accordion').on('hidden.bs.collapse', toggleChevron);
        $('#accordion').on('shown.bs.collapse', toggleChevron);
        $('#accordion').on('shown.bs.collapse', setJKVCollapse);

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
        $(".pagination a").click(function(event) {
            $( "div.se-pre-con" ).fadeIn( "slow" );
        });
        // Submit form when changing panel Filter
        $("#button_change_range_date").unbind("click").click(function(event) {
            check_date();
        });
        $('.show_name_search_result').on('change', function (event) {
            check_date();
        });
        $('#show_my_videos').on('change', function (event) {
            check_date();
        });
        $('#subscribed_video_only').on('change', function (event) {
            check_date();
        });
        $('.class_name_search_result').on('change', function (event) {
            check_date();
        });
        $('.rider_name_search_result').on('change', function (event) {
            check_date();
        });
        $('.rider_number_search_result').on('change', function (event) {
            check_date();
        });
        $('.post_day_search_result').on('change', function (event) {
            check_date();
        });
        $('.horse_name_search_result').on('change', function (event) {
            check_date();
        });

        //Clear all selected data
        $(".clear_all").unbind("click").click(function(event) {
            var id = $(event.target).attr("id");
            switch(id){
                case 'clear_show':
                    $("input[name='show_number']").each(function() {
                        $(this).prop("checked", false);
                    });
                    break;
                case 'clear_class':
                    $("input[name='class_number']").each(function() {
                        $(this).prop("checked", false);
                    });
                    break;
                case 'clear_rider_name':
                    $("input[name='rider_name']").each(function() {
                        $(this).prop("checked", false);
                    });
                    break;
                case 'clear_rider_number':
                    $("input[name='rider_number']").each(function() {
                        $(this).prop("checked", false);
                    });
                    break;
                case 'clear_horse':
                    $("input[name='horse_name']").each(function() {
                        $(this).prop("checked", false);
                    });
                    break;
            }
            check_date();
        });

    });
});

