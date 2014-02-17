define(['jquery', 'underscore', 'backbone', 'text', "text!templates/article_table.html"], function($, _, Backbone, text, articleTableHtml) { 

		var View = Backbone.View.extend({
			events: { },
			initialize: function() {
			},
			render: function() {
				this.$el.html(articleTableHtml);	
				return this;	
			}
		});

	return View;
});
