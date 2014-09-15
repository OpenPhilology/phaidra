define(['jquery', 'underscore', 'backbone', 'utils', 'text!/templates/js/notes-about-word.html'], function($, _, Backbone, Utils, Template) { 

	var View = Backbone.View.extend({
		tagName: 'div', 
		template: _.template(Template),
		events: { 
			'click #parse-vals': 'toggleParse'
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
		toggleParse: function(e) {
			e.preventDefault();
			var link = this.$el.find('#parse-vals');

			link.find('.vals').toggle();
			var toggle = link.find('.vals').is(':visible') ? 'Hide ' : 'See ';
			link.find('strong').html(toggle + gettext('Morphology') + ' &raquo;');
		}
	});

	return View;

});
