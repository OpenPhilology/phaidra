define(['jquery', 'underscore', 'backbone', 'collections', 'views/page', 'views/notes', 'views/knowledge-book-level'], function($, _, Backbone, Collections, PageView, NotesView, KnowledgeView) { 

	var View = Backbone.View.extend({
		events: { },
		initialize: function(options) {
			this.options = options;
			if (!this.options.currentCTS)
				this.options.currentCTS = 'urn:cts:greekLit:tlg0003.tlg001.perseus-grc1:1.89.1';

			// Fetch the list of Documents available to the reader
			this.documents = new Collections.Documents();
			this.documents.on('add', this.initializeReader, this);
			this.documents.fetch();

		},
		render: function() {
			return this;	
		},
		// This is necessary to get the facing page
		initializeReader: function(model) {
			if (model.get('lang') == 'grc') {

				// Now that we know which document we're displaying, listen to it.
				this.model = model;
				this.model.set('currentCTS', this.options.currentCTS);
				this.model.on('change:nextCTS', this.renderPages, this);

				this.model.fetch({
					success: function(model, response, options) {

						// Get CTS of other page
						var rightPage = model.getNextCTS(model.get('currentCTS'));

						if (rightPage)
							model.set('nextCTS', rightPage);
						else
							model.get('nextCTS', model.words.at(0));
					}
				});
			}
		},
		renderPages: function(model, options) {

			// If notes don't exist, render them.
			if (!this.notes) {
				this.notes = new NotesView({
					model: model
				}).render()
					.$el
					.appendTo(this.$el.find('.notes-container'));
			}

			// If knowledge meter doesn't exist, render.
			if (!this.knowledge_view) {
				this.knowledge_view = new KnowledgeView()
					.render()
					.$el
					.appendTo(this.$el);
			}


			// If the views don't exist, render them.
			if (!this.pages) {
				this.pages = {};
				this.pages.left = new PageView({
					model: model,
					side: 'left'
				});
				this.pages.left.render()
					.$el
					.appendTo(this.$el.find('.page-container'));

				this.pages.right = new PageView({
					model: model,
					side: 'right'
				});
				this.pages.right.render()
					.$el
					.appendTo(this.$el.find('.page-container'));
			}
			else {
				// Otherwise, flip the pages
			}
		},
		turnToPage: function(CTS) {
			/*this.$el.find('img').remove();
			this.model.set('currentCTS', CTS);			
			this.model.set('nextCTS', this.model.getNextCTS(CTS));
			*/

			// TODO: Fix navigation
		}
	});

	return View;
});
