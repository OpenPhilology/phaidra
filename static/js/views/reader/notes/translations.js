define(['jquery', 'underscore', 'backbone', 'utils', 'text!/templates/js/reader/notes/translations.html'], function($, _, Backbone, Utils, Template) { 

	var View = Backbone.View.extend({
		tagName: 'div', 
		template: _.template(Template),
		events: { 
			'click a.btn-show-trans': 'showTranslation',
		},
		initialize: function(options) {
			this.options = options;

			// Make a nice map of human-readable names for our translations
		},
		render: function() {

			this.$el.html(this.template({ 
				word: this.model.attributes,
				readableLang: Utils.getReadableLang,
				langs: this.options.langs,
				userLang: this.options.lang || LOCALE,
			}));
			this.$el.find('a[data-lang="' + this.options.lang + '"]').addClass('active');
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
