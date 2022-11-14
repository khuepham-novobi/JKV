odoo.define('jdbw_attendance.datepicker', function (require) {
"use strict";
var core = require('web.core');
var time = require('web.time');
var DateWidgetWeb = require('web.datepicker');
var _t = core._t;
var DateWidget = DateWidgetWeb.DateWidget.include({
    
    init: function(parent, options) {
        this._super(parent, options);
        var l10n = _t.database.parameters;
        if (parent.view.model == "hr.attendance"){
            this.options = _.defaults(options || {}, {
                pickTime: this.type_of_date === 'datetime',
                useSeconds: false,
                startDate: moment({ y: 1900 }),
                endDate: moment().add(200, "y"),
                calendarWeeks: false,
                icons: {
                    time: 'fa fa-clock-o',
                    date: 'fa fa-calendar',
                    up: 'fa fa-chevron-up',
                    down: 'fa fa-chevron-down'
                },
                inline: true,
                sideBySide: true,
                focusOnShow: false,
                language : moment.locale(),
                format : time.strftime_to_moment_format((this.type_of_date === 'datetime')? (l10n.date_format + ' ' + l10n.time_format) : l10n.date_format),
            });
        }
        else{
            this.options = _.defaults(options || {}, {
                pickTime: this.type_of_date === 'datetime',
                useSeconds: this.type_of_date === 'datetime',
                startDate: moment({ y: 1900 }),
                endDate: moment().add(200, "y"),
                calendarWeeks: false,
                icons: {
                    time: 'fa fa-clock-o',
                    date: 'fa fa-calendar',
                    up: 'fa fa-chevron-up',
                    down: 'fa fa-chevron-down'
                },
                focusOnShow: false,
                language : moment.locale(),
                format : time.strftime_to_moment_format((this.type_of_date === 'datetime')? (l10n.date_format + ' ' + l10n.time_format) : l10n.date_format),
            });
        }
    },
    
});
});
