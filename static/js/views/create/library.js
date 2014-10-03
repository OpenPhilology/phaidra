define(['jquery', 'underscore', 'backbone', 'collections/documents', 'text!/templates/js/create/library-edition.html'], function($, _, Backbone, DocumentsCollection, Template) { 

	var View = Backbone.View.extend({
		events: { 
			//'click a.edition': 'createPersonalEdition'
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
			if (model.get('lang') === 'grc') {
				var compiled = _.template(Template);
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
		},
		submitModal: function(e) {

		}
	});

	return View;
});
