define(['jquery', 'underscore', 'backbone', 'views/reader/reader', 'views/create/library'], function($, _, Backbone, ReaderView, LibraryView) { 

	return Backbone.Router.extend({
		initialize: function() {
			this.route(/^(.*?)\/reader$/, 'showLibrary');
			this.route(/^(.*?)\/reader\/(.*?)$/, 'updateReader');
		},
		showLibrary: function(lang) {
			if (!this.library_view)
				this.library_view = new LibraryView({ el: '#library' }).render();

			this.library_view.$el.show();

			if (this.reader_view) 
				this.reader_view.$el.hide();

		},
		updateReader: function(lang, CTS) {
			if (!this.reader_view) 
				this.reader_view = new ReaderView({ el: '#reader', CTS: CTS }).render();
			else
				this.reader_view.turnToPage(CTS);

			this.reader_view.$el.show();

			// Hide the library if we're coming from there
			if (this.library_view) {
				this.library_view.$el.hide();
			}
		}
	});
	
});
