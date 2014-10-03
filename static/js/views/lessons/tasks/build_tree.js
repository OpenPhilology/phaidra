define(['jquery', 'underscore', 'backbone', 'models/word', 'collections/words', 'utils', 'text!/templates/js/lessons/tasks/build_tree.html'], function($, _, Backbone, WordModel, WordsCollection, Utils, Template) {

	var View = Backbone.View.extend({
		tagName: 'div',
		className: 'subtask',
		template: _.template(Template),
		initialize: function(options) {
			console.log("init");
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
