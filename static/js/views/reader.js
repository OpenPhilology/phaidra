define(['jquery', 'underscore', 'backbone', 'collections', 'views/page', 'views/notes', 'views/knowledge-book-level'], function($, _, Backbone, Collections, PageView, NotesView, KnowledgeView) { 

	var View = Backbone.View.extend({
		events: { },
		initialize: function(options) {
			this.options = options;

			// Fetch the list of Documents available to the reader
			this.documents = new Collections.Documents();
			this.documents.on('add', this.initializeReader, this);
			this.documents.fetch();

			// Bind view context to our model population callbacks
			_.bindAll(this, "fetchSuccess", "fetchError");

		},
		render: function() {
			// Render early what we can
			if (!this.knowledge_view) {
				this.knowledge_view = new KnowledgeView()
					.render()
					.$el
					.appendTo(this.$el);
			}

			return this;	
		},
		initializeReader: function(model) {

			// Fetch the document indicated by the URL
			var doc = this.options.CTS.split(':')[3];

			if (model.get('CTS').indexOf(doc) !== -1) {
				this.model = model;
				this.model.fetch({
					success: this.fetchSuccess,
					error: this.fetchError
				});
			}
		},
		fetchSuccess: function(model, options) {
			// Successfully got the words we need for our initial render
			this.renderPages(model);	
		},
		fetchError: function(model, options) {
			console.log("error fetching ", model);
		},
		renderPages: function(model, options) {
			if (!this.notes) {
				this.notes = new NotesView({
					model: model
				}).render()
					.$el
					.appendTo(this.$el.find('.notes-container'));
			}

			// If the views don't exist, render them.
			if (!this.pages) {
				this.pages = {};

				this.pages.left = new PageView({
					model: model,
					side: 'left',
					CTS: this.options.CTS
				});
				this.pages.left.render()
					.$el
					.appendTo(this.$el.find('.page-container'));

				this.pages.right = new PageView({
					model: model,
					side: 'right',
					CTS: this.model.getNextCTS(this.options.CTS)
				});
				this.pages.right.render()
					.$el
					.appendTo(this.$el.find('.page-container'));
			}
		},
		turnToPage: function(CTS) {
			this.options.CTS = CTS;
			this.pages.left.turnToPage(CTS);
			this.pages.right.turnToPage(this.model.getNextCTS(CTS));
		}
	});

	return View;
});
