define(['jquery', 'underscore', 'backbone', 'collections', 'text!/templates/js/library-edition.html'], function($, _, Backbone, Collections, EditionTemplate) { 

	var View = Backbone.View.extend({
		events: { },
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

				this.$el.append(html);
			}

			return this;
		},
	});

	return View;
});
