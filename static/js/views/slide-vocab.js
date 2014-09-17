define(['jquery', 'underscore', 'backbone', 'models', 'collections', 'text!/templates/js/slide-vocab.html'], function($, _, Backbone, Models, Collections, Template) {
	var View = Backbone.View.extend({
		tagName: 'div',
		className: 'slide-unit',
		template: _.template(Template),
		events: { },
		initialize: function(options) {
			this.options = options;
			this.model.on('change:populated', this.render, this);
		},
		render: function() {
			this.$el.html(this.template(this.model.attributes));
			return this;	
		}
	});

	return View;
});
