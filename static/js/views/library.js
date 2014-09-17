define(['jquery', 'underscore', 'backbone', 'collections', 'text!/templates/js/library-edition.html'], function($, _, Backbone, Collections, EditionTemplate) { 

	var View = Backbone.View.extend({
		events: { 
			'click a.edition': 'createPersonalEdition'
		},
		initialize: function(options) {
			var that = this;
			this.options = options;

			// Create/Populate necessary models and collections
			this.documents = new Collections.Documents();
			this.documents.bind('add', this.renderDocument, this);
			this.documents.fetch();

		},
		render: function() {
			return this;	
		},
		renderDocument: function(model) {
			if (model.get('lang') === 'grc') {
				var compiled = _.template(EditionTemplate);
				var html = compiled({ model: model });

				this.$el.find('.editions').append(html);
			}

			return this;
		},
		renderPersonalEdition: function(collection) {
			console.log(collection);
		},
		createPersonalEdition: function(e) {
			e.preventDefault();
			var target = e.target.getAttribute('href');

			// If the user doesn't already have a personal edition for this work, prompt them to make one
			this.userDocuments = new Collections.UserDocuments();
			this.userDocuments.fetch({ success: this.renderPersonalEdition.bind(this) });

			// Otherwise, just forward them to the Reader*/
		},
		submitModal: function(e) {

		}
	});

	return View;
});
