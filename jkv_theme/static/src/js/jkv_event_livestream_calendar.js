odoo.define('jkv_theme.jkv_livestream_calendar', function (require) {
    "use strict";
     var ajax = require('web.ajax');
     $(document).ready(function () {
         var jkvCalendar = document.getElementById("jkv_full_livestream_calendar");
         if(jkvCalendar){
            ajax.jsonRpc("/action_get_event_livestream_calendar", 'call').then(function(events){
                $('#jkv_full_livestream_calendar').fullCalendar({
                                        header: {
                                                right: 'prev,next',
                                                center: 'title',
                                                left: 'month,basicWeek'
                                            },
                                        events: events,
                                        eventClick: function(event) {
                                            if (event.url) {
                                              window.open(event.url);
                                              return false;
                                            }
                                         }
                });
            });
         }
     });
});