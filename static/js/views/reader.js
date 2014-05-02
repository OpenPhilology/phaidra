define(['jquery', 'underscore', 'backbone', 'collections', 'views/page', 'views/notes', 'views/knowledge-book-level'], function($, _, Backbone, Collections, PageView, NotesView, KnowledgeView) { 

	var View = Backbone.View.extend({
		events: { },
		initialize: function() {
			var that = this;

			// Create an empty collection of words, so views can update based on changes to it
			this.collection = new Collections.Words();

			// Start by getting our reader content and building a table of contents
			this.buildBook();

			this.turnToPage('urn:cts:greekLit:tlg0003.tlg001.perseus-grc1:1.89.1');

			// Render the notes viewer at the bottom of the screen
			if (!this.notes) {
				this.notes = new NotesView({
					collection: this.collection
				}).render()
					.$el
					.appendTo(this.$el.find('.notes-container'));
			}

			// Knowledge Meter at bottom of reader
			if (!this.knowledge) {
				this.knowledge = new KnowledgeView()
					.render()
					.$el
					.appendTo(this.$el);
			}
		},
		render: function() {
			return this;	
		},
		/*
		*	Grab the data we need to build their book. Specifically have to grab this data
		*	for navigation, since we can't predict the next resource by CTS alone.
		*	TODO: Make a book model? Overkill/Unnecessary?
		*/
		buildBook: function() {
			// Thuc hardcoded, TODO: generalize for translations
			var url = '/api/v1/document/0/?format=json';
			var that = this;

			$.ajax({
				url: url,
				async: false,
				dataType: 'json',
				success: function(book) {
					// Keep a reference to the book's metadata
					that.book = book;

					// Build our collection of words
					for (var i = 0; i < book.sentences.length; i++) {
						var tokens = $.trim(book.sentences[i]["sentence"]).split(' ');

						$.each(tokens, function(j, token) {
							that.collection.add({
								'value': token,
								'lang': 'grc',
								'sentenceURI': book.sentences[i]["resource_uri"],
								'sentenceCTS': book.sentences[i]["CTS"],
								'CTS': book.sentences[i]["CTS"] + ':' + (j + 1)
							});
						});
					}
				}
			});
		},
		turnToPage: function(cts) {

			// Get the CTS ref after the one passed in, to build facing page
			var i = _.findWhere(this.book.sentences, { CTS: cts });
			var j = this.book.sentences.indexOf(i) + 1;

			// Next CTS is...
			var ctsNext = this.book.sentences[j]["CTS"];

			var that = this;

			// Render pages if not yet appended to DOM
			if (!this.pages) {
				this.pages = {};
				this.pages.left = new PageView({ 
					collection: that.collection, 
					cts: cts,
					side: 'left' 
				}).render()
					.$el
					.appendTo(this.$el.find('.page-container'));

				this.pages.right = new PageView({ 
					collection: that.collection,
					cts: ctsNext,
					side: 'right' 
				}).render()
					.$el
					.appendTo(this.$el.find('.page-container'));
			}
			// Otherwise, turn the pages
			else {
				this.pages.left.turnPage(cts);
				this.pages.right.turnPage(ctsNext);
			}
		}
	});

	return View;
});
