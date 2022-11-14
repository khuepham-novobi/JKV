odoo.define('jkv_website_sale.search_input', function(require) {
    var Widget = require('web.Widget');
    var ajax = require('web.ajax');
    var SearchInput = Widget.extend({
        init: function(parent, options) {
            this._super.apply(this, arguments);
            this.model = options.model;
            this.input_label = options.input_label;
            this.operator = 'ilike';
            this.order = 'name ASC';
            this.source = [];
            var self = this;
            $("li."+this.input_label).each(function(){
                txt = $(this).text().trim();
                val = $(this).find("input[class='"+self.input_label+"']").val();
                self.source.push({
                    label:txt,
                    value: txt,
                    get_value: val
                })
            })
            /*
            switch (this.input_label) {
                case 'show_name_search_result':
                    this.fields = ['name','show_number'];
                    this.field_domain = 'name';
                    $(".show_name_search_result").each(function(){
                        self.source.push({label:$(this).parent().find('.data_show').text(),value:$(this).parent().find('.data_show').text(),get_value:$(this).val()})
                    })
                    break;
                case 'class_name_search_result':
                    this.fields = ['name','class_number'];
                    this.field_domain = 'name';
                     $(".class_name_search_result").each(function(){
                        self.source.push({label:$(this).parent().find('.data_show').text(),value:$(this).parent().find('.data_show').text(),get_value:$(this).val()})
                    })
                    break;
                case 'rider_name_search_result':
                    this.fields = ['rider_name'];
                    this.field_domain = 'rider_name';
                    this.order = 'rider_name ASC';
                    break;
                case 'rider_number_search_result':
                    this.fields = ['rider_number'];
                    this.field_domain = 'rider_number';
                    this.operator = '=';
                    this.order = '';
                    break;
                case 'horse_name_search_result':
                    this.fields = ['horse_name'];
                    this.field_domain = 'horse_name';
                    this.order = '';
                    break;
            }*/
        },
        start: function () {
            var self = this;
            this.$input = this.$el.find('input');
            this.$input.autocomplete({
                source:function(request,response){
                    var data = _.filter(self.source,function(e){
                        return e['value'].toLowerCase().indexOf(request.term.toLowerCase()) !== -1 ||
                            e['value'].toUpperCase().indexOf(request.term.toUpperCase()) !== -1;
                    })
                    response(data);
                    /*
                    ajax.jsonRpc("/web/dataset/call_kw", 'call', {
                        model:self.model,
                        method: 'search_read',
                        args: [],
                        kwargs: {
                            fields: self.fields,
                            domain: [[self.field_domain,self.operator,request.term]],
                            order: self.order
                        }
                    }).then(function(result){
                        var data = []
                        switch (self.input_label) {
                            case 'show_name_search_result':
                                data = _.map(result,function(e){return {label:e['name'],value:e['name'],get_value:e['id']}});
                                break;
                            case 'class_name_search_result':
                                data = _.map(result,function(e){return {label:e['name'],value:e['name'],get_value:e['id']}});
                                break;
                            case 'rider_name_search_result':
                                data = _.uniq(_.map(result,function(e){return e['rider_name']}));
                                data = _.map(data,function(e){return {label:e,value:e,get_value:e}});
                                break;
                            case 'rider_number_search_result':
                                result = _.sortBy(result, 'rider_number');
                                data = _.uniq(_.map(result,function(e){return e['rider_number']}));
                                data = _.map(data,function(e){return {label:e,value:e,get_value:e}});
                                break;
                            case 'horse_name_search_result':
                                result = _.sortBy(result, 'horse_name');
                                data = _.uniq(_.map(result,function(e){return e['horse_name']}));
                                data = _.map(data,function(e){return {label:e,value:e,get_value:e}});
                                break;
                        }
                        response(data);
                    })*/
                },
                select: function(event,ui) {
                    var value = ui.item.get_value.toString();
                    $('.'+self.input_label+"[value='"+value+"']").prop("checked", true);
                    $('.'+self.input_label+"[value='"+value+"']").trigger('change');
                    //$('#form-panel-search-result').submit();
                },
            })
        },
    })
    $(document).ready(function () {
        $('.search_input').each(function () {
            var $elem = $(this);
            var search = new SearchInput(null, {'model':$elem.attr('data-model'),'input_label':$elem.attr('data-label')});
            search.attachTo($elem);
        })
    })

})