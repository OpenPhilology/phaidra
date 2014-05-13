define(['jquery', 'underscore', 'backbone', 'utils', 'text!templates/grammar-display.html'], function($, _, Backbone, Utils, Template) { 

	var View = Backbone.View.extend({
		events: { },
		template: _.template(Template),
		tagName: 'div',
		initialize: function(options) {
			var that = this;
			this.options = options;
		},
		render: function() {
			var that = this;

			this.$el.html(this.template({
				content: Utils.Content, 
				smyth: Utils.Smyth[0],
				selected: that.options.smyth
			}));

			return this;	
		}
	});

	return View;
});
