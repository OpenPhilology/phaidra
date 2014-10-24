define(['jquery', 
	'underscore', 
	'backbone', 
	'collections/documents',
	'collections/topics',
	'views/reader/reader', 
	'views/create/library'], 
	function($, _, Backbone, DocumentsCollection, TopicsCollection, ReaderView, LibraryView) { 

		return Backbone.Router.extend({
			initialize: function() {
				this.route(/^(.*?)\/reader\/(.*?)$/, 'showLibrary');
				this.route(/^(.*?)\/reader\/(.+)$/, 'updateReader');

				// Initialize Models and Collections used by Reader and its Subviews
				this.documents = new DocumentsCollection();
				this.topics = new TopicsCollection();
				this.topics.setEndpointLimit(0);
				this.topics.fetch();
			},
			showLibrary: function(lang) {
				if (!this.library_view)
					this.library_view = new LibraryView({ el: '#library' }).render();

				this.library_view.$el.show();

				if (this.reader_view) 
					this.reader_view.$el.hide();

			},
			updateReader: function(lang, CTS) {
				if (!this.reader_view) { 
					this.reader_view = new ReaderView({ 
						el: '#reader', 
						CTS: CTS, 
						documents: this.documents,
						topics: this.topics
					}).render();
				}
				else {
					this.reader_view.turnToPage(CTS);
				}

				this.reader_view.$el.show();

				// Hide the library if we're coming from there
				if (this.library_view) {
					this.library_view.$el.hide();
				}
			}
		});
	}
);
