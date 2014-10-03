define(['jquery', 'underscore', 'backbone', 'models', 'collections', 'utils', 'text!/templates/js/task-translate_word.html'], function($, _, Backbone, Models, Collections, Utils, Template) {

	var View = Backbone.View.extend({
		template: _.template(Template),
		initialize: function(options) {

		},
		render: function() {
			this.$el.html(this.template({
				model: this.model
			}));

			return this;
		}
	});

	return View;
});
