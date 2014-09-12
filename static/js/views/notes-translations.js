define(['jquery', 'underscore', 'backbone', 'utils', 'text!/templates/js/notes-translations.html'], function($, _, Backbone, Utils, Template) { 

	var View = Backbone.View.extend({
		tagName: 'div', 
		template: _.template(Template),
		events: { 
			'click a.btn-show-trans': 'showTranslation',
		},
		initialize: function(options) {
			this.options = options;
		},
		render: function() {
			this.$el.html(this.template({ 
				word: this.model.attributes,
				langs: this.options.langs,
				lang: this.options.lang || locale.split('-')[0],
				grammar: this.model.getGrammar()
			}));
			return this;	
		},
		showTranslation: function(e) {
			e.preventDefault();
			this.options.lang = $(e.target).attr('data-lang');
			this.render();
		}
	});

	return View;

});
