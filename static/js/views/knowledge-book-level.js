define(['jquery', 'underscore', 'backbone', 'text!templates/knowledge-book-level.html'], function($, _, Backbone, KnowledgeTemplate) { 
	var View = Backbone.View.extend({
		tagName: 'div', 
		className: 'row knowledge-container',
		template: _.template(KnowledgeTemplate),
		events: {},
		initialize: function(options) {
			this.$el.find('div').tooltip();
		},
		render: function() {
			this.$el.html(this.template());
			return this;
		}
	});

	return View;
});
