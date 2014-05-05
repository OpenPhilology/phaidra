define(['jquery', 'underscore', 'backbone', 'collections', 'views/page', 'views/notes', 'views/knowledge-book-level'], function($, _, Backbone, Collections, PageView, NotesView, KnowledgeView) { 

	var View = Backbone.View.extend({
		events: { },
		initialize: function(options) {
			var that = this;

			// Create an empty collection of words, so views can update based on changes to it
			this.collection = new Collections.Words();

			// Start by getting our reader content and building a table of contents
			this.buildBook();

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
					// Keep a reference to the book's metadata -- important for turning pages
					that.collection._meta = {};
					that.collection._meta.book = book;

					// Build our collection of words
					for (var i = 0; i < book.sentences.length; i++) {
						var tokens = $.trim(book.sentences[i]["sentence"]).split(' ');

						$.each(tokens, function(j, token) {
							var next, prev;

							if (book.sentences[i-2])
								prev = book.sentences[i-1]["CTS"];	
							if (book.sentences[i+2])
								next = book.sentences[i+1]["CTS"];

							that.collection.add({
								'value': token,
								'lang': book.lang,
								'sentenceURI': book.sentences[i]["resource_uri"],
								'sentenceCTS': book.sentences[i]["CTS"],
								'nextSentenceCTS': next || undefined,
								'prevSentenceCTS': prev || undefined,
								'CTS': book.sentences[i]["CTS"] + ':' + (j + 1)
							});
						});
					}
				}
			});
		},
		turnToPage: function(cts) {

			if (cts == undefined)
				cts = this.collection.at(0).get('sentenceCTS');

			// Get the CTS ref after the one passed in, to build facing page
			var i = _.findWhere(this.collection._meta.book.sentences, { CTS: cts });
			var j = this.collection._meta.book.sentences.indexOf(i) + 1;

			// Next CTS is...
			var ctsNext = this.collection._meta.book.sentences[j]["CTS"];

			var that = this;

			// Render pages if not yet appended to DOM
			if (!this.pages) {
				this.pages = {};
				this.pages.left = new PageView({ 
					collection: that.collection, 
					cts: cts,
					side: 'left' 
				});
				this.pages.left.render()
					.$el
					.appendTo(this.$el.find('.page-container'));

				this.pages.right = new PageView({ 
					collection: that.collection,
					cts: ctsNext,
					side: 'right' 
				});
				this.pages.right.render()
					.$el
					.appendTo(this.$el.find('.page-container'));
			}
			// Otherwise, turn the pages
			else {
				this.pages.left.turnToPage(cts);
				this.pages.right.turnToPage(ctsNext);
			}
		}
	});

	return View;
});
