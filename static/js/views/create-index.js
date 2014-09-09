define(['jquery', 'underscore', 'backbone', 'utils', 'text!/templates/js/create-edition.html'], function($, _, Backbone, Utils, Template) { 

	var View = Backbone.View.extend({
		events: { 
		},
		template: _.template(Template),
		tagName: 'div',
		className: 'col-md-4',
		initialize: function(options) {
			var that = this;
			this.options = options;
		},
		render: function() {
			var that = this;
			this.$el.html(this.template({
				model: this.model
			}));

			return this;	
		}
	});

	return View;
});
