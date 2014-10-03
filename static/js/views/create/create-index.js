define(['jquery', 'underscore', 'backbone', 'collections/documents', 'utils', 'text!/templates/js/create/create-edition.html'], function($, _, Backbone, DocumentsCollection, Utils, EditionTemplate) { 

	var View = Backbone.View.extend({
		events: { 
			'click #language-selector a': 'switchLanguage'
		},
		initialize: function(options) {
			var that = this;
			this.options = options;

			// Create/Populate necessary models and collections
			this.documents = new DocumentsCollection();
			this.documents.bind('add', this.renderDocument, this);
			this.documents.fetch();
		},
		render: function() {
			return this;	
		},
		renderDocument: function(model) {
			var compiled = _.template(EditionTemplate);
			var html = compiled({ model: model });

			this.$el.find('#create-editions').append(html);
			return this;
		},
		switchLanguage: function(e) {
			e.preventDefault();
			var target = e.target.dataset.lang;
			this.$el.find('#language-selector .active').removeClass('active');
			$(e.target).addClass('active');

			// Hide editions not in this language
			var els = this.$el.find('#create-editions div[data-lang]');
			$.each(els, function(i, el) {
				if (el.dataset.lang === target)
					$(el).show();
				else
					$(el).hide();
			});

			// Switch the active language in the menu
			this.renderLanguageSelector(e);
		},
		renderLanguageSelector: function() {
			var humanReadable = this.$el.find('#language-selector .active').html();
			this.$el.find('#language-selector .btn-group > button').eq(0).html(humanReadable);
		}
	});

	return View;
});
