define(['jquery', 'underscore', 'backbone', 'models', 'collections', 'text!/templates/js/slide-last.html'], function($, _, Backbone, Models, Collections, Template) {
	var View = Backbone.View.extend({
		tagName: 'div',
		className: 'slide-unit',
		template: _.template(Template),
		events: { },
		initialize: function(options) {
			this.options = options;
		},
		render: function() {
			//this.$el.html(this.template(this.model.attributes));
			this.$el.html('Last slide, here\'s a summary of what you learned.');
			
			return this;
		},
		navigate: function(e) {
			e.preventDefault();
		}
	});

	return View;
});
