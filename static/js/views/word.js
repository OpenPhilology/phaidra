define(['jquery', 'underscore', 'backbone', 'text!/templates/js/word.html'], function($, _, Backbone, WordTemplate) { 

	var View = Backbone.View.extend({
		events: { 
		},
		initialize: function(options) {
			this.$el = $(_.template(WordTemplate, this.model.attributes });
		},
		render: function() {
			return this;
		}
	});

	return View;
});
