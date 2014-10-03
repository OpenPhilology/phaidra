define(['jquery', 'underscore', 'backbone', 'text!/templates/js/knowledge-book-level.html'], function($, _, Backbone, KnowledgeTemplate) { 
	var View = Backbone.View.extend({
		tagName: 'div', 
		className: 'row knowledge-container',
		template: _.template(KnowledgeTemplate),
		events: {},
		initialize: function(options) {
		},
		render: function() {
			this.$el.html(this.template());
			this.$el.find('div').tooltip();
			return this;
		}
	});

	return View;
});
