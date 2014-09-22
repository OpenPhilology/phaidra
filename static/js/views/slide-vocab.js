define(['jquery', 'underscore', 'backbone', 'models', 'collections', 'text!/templates/js/slide-vocab.html'], function($, _, Backbone, Models, Collections, Template) {
	var View = Backbone.View.extend({
		tagName: 'div',
		className: 'slide-unit',
		template: _.template(Template),
		events: { },
		initialize: function(options) {
			console.log("vocab slide called");
			this.options = options;
			this.model.on('change:populated', this.render, this);
		},
		render: function() {
			console.log(this.model.get('vocab'));
			this.$el.html(this.template({
				model: this.model
			}));
			return this;	
		}
	});

	return View;
});
