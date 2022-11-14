odoo.define('theme_furnito.theme_furnito_frontend_js', function(require) {
    'use strict';

    var animation = require('web_editor.snippets.animation');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var _t = core._t;

    animation.registry.theme_furnito_product_category_slider = animation.Class.extend({
        selector: ".oe_pro_cat_slider",
        start: function(editable_mode) {
            var self = this;
            if (editable_mode) {
                $('.oe_pro_cat_slider .owl-carousel').empty();
            }
            if (!editable_mode) {
                var slider_type = self.$target.attr('data-prod-cat-slider-type');
                $.get("/theme_furnito/pro_get_dynamic_slider", {
                    'slider-type': self.$target.attr('data-prod-cat-slider-type') || '',
                }).then(function(data) {
                    if (data) {
                        self.$target.empty();
                        self.$target.append(data);
                        $(".oe_pro_cat_slider").removeClass('hidden');

                        ajax.jsonRpc('/theme_furnito/pro_image_effect_config', 'call', {
                            'slider_type': slider_type
                        }).done(function(res) {
                            _.each(self.$target.find('.cs-product'), function(k, v) {
                                if ($(k).find('.o_rating_star_card')) {
                                    var input_val = $(k).find('.o_rating_star_card').find("input").data('default');
                                    if (input_val > 0) {
                                        var rating = require('rating.rating');
                                        var rating_star = new rating.RatingStarWidget(this, {
                                            'rating_default_value': input_val,
                                            'rating_disabled': true,
                                        });
                                        if (rating_star) {
                                            $(k).find('.rating').empty();
                                            rating_star.appendTo($(k).find('.rating'));
                                        }
                                    }
                                }
                            });

                            $('div#' + res.s_id).owlCarousel({
                                margin: 10,
                                responsiveClass: true,
                                items: res.counts,
                                loop: true,
                                autoPlay: res.auto_rotate && res.auto_play_time,
                                stopOnHover: true,
                                navigation: true,
                                responsive: {
                                    0: {
                                        items: 1,
                                    },
                                    420: {
                                        items: 2,
                                    },
                                    768: {
                                        items: 3,
                                    },
                                    1000: {
                                        items: res.counts,
                                    },
                                    1500: {
                                        items: res.counts,
                                    },
                                },
                            });
                        });
                    }
                });
            }
        }
    });

    animation.registry.theme_furnito_brand_custom_slider = animation.Class.extend({
        selector: ".furnito_theme_brand_slider",
        start: function(editable_mode) {
            var self = this;
            if (editable_mode) {
                $('div#theme_furnito_brand_slider').empty();
            }
            if (!editable_mode) {
                $.get("/furnito_theme/get_brand_slider", {
                    'brand_count': self.$target.attr('data-brand-count') || 0,
                    'brand_label': self.$target.attr('data-brand-label') || '',
                }).then(function(data) {
                    if (data) {
                        self.$target.empty();
                        self.$target.append(data);
                        $(".furnito_theme_brand_slider").removeClass('hidden');
                        $('div#theme_furnito_brand_slider').owlCarousel({
                            margin: 10,
                            loop: true,
                            autoPlay: 9000,
                            stopOnHover: true,
                            navigation: true,
                            responsiveClass: true,
                            responsive: {
                                0: {
                                    items: 1,
                                },
                                420: {
                                    items: 2,
                                },
                                768: {
                                    items: 4,
                                },
                                1000: {
                                    items: 6,
                                },
                                1500: {
                                    items: 6,
                                },
                            },
                        });
                    }
                });
            }
        }
    });

    animation.registry.theme_furnito_blog_custom_snippet = animation.Class.extend({
        selector: ".furnito_theme_blog_slider",
        start: function(editable_mode) {
            var self = this;
            if (editable_mode) {
                $('.furnito_theme_blog_slider .owl-carousel').empty();
            }
            if (!editable_mode) {
                var slider_type = self.$target.attr('data-blog-slider-type');
                $.get("/theme_furnito/blog_get_dynamic_slider", {
                    'slider-type': self.$target.attr('data-blog-slider-type') || '',
                }).then(function(data) {
                    if (data) {
                        self.$target.empty();
                        self.$target.append(data);
                        $(".furnito_theme_blog_slider").removeClass('hidden');

                        ajax.jsonRpc('/theme_furnito/blog_image_effect_config', 'call', {
                            'slider_type': slider_type
                        }).done(function(res) {

                            $('div#' + res.s_id).owlCarousel({
                                margin: 10,
                                responsiveClass: true,
                                items: res.counts,
                                loop: true,
                                autoPlay: res.auto_rotate && res.auto_play_time,
                                stopOnHover: true,
                                navigation: true,
                                responsive: {
                                    0: {
                                        items: 1,
                                    },
                                    420: {
                                        items: 2,
                                    },
                                    768: {
                                        items: res.counts,
                                    },
                                    1000: {
                                        items: res.counts,
                                    },
                                    1500: {
                                        items: res.counts,
                                    }
                                },
                            });
                        });

                    }
                });
            }
        }
    });

    animation.registry.theme_furnito_multi_cat_custom_snippet = animation.Class.extend({
        selector: ".oe_multi_category_slider",
        start: function(editable_mode) {
            var self = this;
            if (editable_mode) {
                $('.oe_multi_category_slider .owl-carousel').empty();
            }
            if (!editable_mode) {
                var slider_type = self.$target.attr('data-multi-cat-slider-type');
                $.get("/theme_furnito/product_multi_get_dynamic_slider", {
                    'slider-type': self.$target.attr('data-multi-cat-slider-type') || '',
                }).then(function(data) {
                    if (data) {
                        self.$target.empty();
                        self.$target.append(data);
                        $(".oe_multi_category_slider").removeClass('hidden');

                        ajax.jsonRpc('/theme_furnito/product_multi_image_effect_config', 'call', {
                            'slider_type': slider_type
                        }).done(function(res) {
                            _.each(self.$target.find('.cs-product'), function(k, v) {
                                if ($(k).find('.o_rating_star_card')) {
                                    var input_val = $(k).find('.o_rating_star_card').find("input").data('default');
                                    if (input_val > 0) {
                                        var rating = require('rating.rating');
                                        var rating_star = new rating.RatingStarWidget(this, {
                                            'rating_default_value': input_val,
                                            'rating_disabled': true,
                                        });
                                        if (rating_star) {
                                            $(k).find('.rating').empty();
                                            rating_star.appendTo($(k).find('.rating'));
                                        }
                                    }
                                }
                            });
                            $('.multi_hide .owl-carousel').owlCarousel({
                                margin: 10,
                                responsiveClass: true,
                                items: 4,
                                loop: true,
                                autoPlay: res.sliding_speed,
                                stopOnHover: true,
                                navigation: true,
                                responsive: {
                                    0: {
                                        items: 1,
                                    },
                                    420: {
                                        items: 2,
                                    },
                                    767: {
                                        items: 3,
                                    },
                                    1000: {
                                        items: 4,
                                    },
                                    1500: {
                                        items: 4,
                                    },
                                },
                            });
                        });

                    }
                });
            }
        }
    });

    animation.registry.theme_furnito_category_slider = animation.Class.extend({
        selector: ".oe_cat_slider",
        start: function(editable_mode) {
            var self = this;
            if (editable_mode) {
                $('#theme_furnito_custom_category_slider').empty();
                var cat_name = _t("Category Slider")
                $('#theme_furnito_custom_category_slider').empty().append('<div class="container">\
                                                    <div class="row our-categories">\
                                                        <div class="col-md-12">\
                                                            <div class="title-block">\
                                                                <h4 class="section-title style1">\
                                                                    <span>' + cat_name + '</span>\
                                                                </h4>\
                                                            </div>\
                                                        </div>\
                                                    </div>\
                                                </div>');

            }
            if (!editable_mode) {
                var slider_id = self.$target.attr('data-cat-slider-id');
                $.get("/theme_furnito/category_get_dynamic_slider", {
                    'slider-id': self.$target.attr('data-cat-slider-id') || '',
                }).then(function(data) {
                    if (data) {
                        self.$target.empty();
                        self.$target.append(data);
                        $(".oe_cat_slider").removeClass('hidden');

                        ajax.jsonRpc('/theme_furnito/category_image_effect_config', 'call', {
                            'slider_id': slider_id
                        }).done(function(res) {
                            $('div#' + res.s_id).owlCarousel({
                                loop: true,
                                navigation: true,
                                margin: 10,
                                responsiveClass: true,
                                items: res.counts,
                                autoPlay: res.auto_rotate && res.auto_play_time,
                                stopOnHover: true,
                                responsive: {
                                    0: {
                                        items: 1,
                                    },
                                    420: {
                                        items: 2,
                                    },
                                    768: {
                                        items: 3,
                                    },
                                    1000: {
                                        items: res.counts,
                                    },
                                    1500: {
                                        items: res.counts,
                                    },
                                },
                            });
                        });
                    }
                });
            }
        }
    });

    animation.registry.theme_furnito_featured_product_slider = animation.Class.extend({
        selector: ".oe_featured_prod_slider",
        start: function(editable_mode) {
            var self = this;
            if (editable_mode) {
                $('div#div_theme_furnito_custom_featured_product_theme').empty();
            }
            if (!editable_mode) {
                var slider_id = self.$target.attr('data-featured_prod-slider-id');
                $.get("/theme_furnito/featured_product_get_dynamic_slider", {
                    'slider-id': self.$target.attr('data-featured-prod-slider-id') || '',
                }).then(function(data) {
                    if (data) {
                        self.$target.empty();
                        self.$target.append(data);
                        $(".oe_featured_prod_slider").removeClass('hidden');
                    }
                });
            }
        }
    });

});