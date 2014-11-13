define(['jquery', 'underscore', 'backbone', 'utils', 'text!/templates/js/reader/notes/build-parse-tree.html'], function($, _, Backbone, Utils, Template) { 

	var View = Backbone.View.extend({
		tagName: 'div', 
		template: _.template(Template),
		events: { 
		},
		initialize: function(options) {
			this.options = options;
		},
		render: function() {
			this.$el.html(this.template({ 
				word: this.model.attributes,
				langs: this.options.langs,
				lang: this.options.lang || LOCALE,
			}));
			return this;	
		}
	});

	return View;

});
