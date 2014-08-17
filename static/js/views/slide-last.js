define(['jquery', 'underscore', 'backbone', 'models', 'collections', 'text!/templates/js/slide-last.html'], function($, _, Backbone, Models, Collections, Template) {
	var View = Backbone.View.extend({
		tagName: 'div',
		className: 'slide-unit',
		template: _.template(Template),
		events: { },
		initialize: function(options) {
			this.options = options;
			this.collection = options.collection;
			this.collection.on('completed', this.draw, this); 
		},
		render: function() {
			return this;
		},
		draw: function() {

			this.$el.html(this.template({
				"stats": this.collection.makeStats()
			}));
			
		}
	});

	return View;
});
