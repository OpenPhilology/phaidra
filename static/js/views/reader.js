define(['jquery', 'underscore', 'backbone', 'collections', 'views/page', 'views/notes', 'views/knowledge-book-level'], function($, _, Backbone, Collections, PageView, NotesView, KnowledgeView) { 

	var View = Backbone.View.extend({
		events: { },
		initialize: function(options) {
			var that = this;

			// Create an empty collection of words, so views can update based on changes to it
			this.collection = new Collections.Words();
			this.collection.buildBook('urn:cts:greekLit:tlg0003.tlg001.perseus-grc1:1');

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
		turnToPage: function(CTS) {

			// Turning pages by CTS is just gross...
			var that = this, uri, next_uri;
			if (CTS == undefined) {
				uri = this.collection._meta.sentence_resource_uris[0];
				next_uri = this.collection._meta.sentence_resource_uris[1];
			}
			else {
				this.collection.addSentence({ sentenceCTS: CTS });
				uri = this.collection.findWhere({ sentenceCTS: CTS }).get('sentence_resource_uri');
				var index = this.collection._meta.sentence_resource_uris.indexOf(uri) + 1; 
				next_uri = this.collection._meta.sentence_resource_uris[index];
			}

			this.$el.find('.loader').remove();

			// Render pages if not yet appended to DOM
			if (!this.pages) {
				this.pages = {};
				this.pages.left = new PageView({ 
					collection: that.collection, 
					sentence_resource_uri: uri,
					side: 'left' 
				});
				this.pages.left.render()
					.$el
					.appendTo(this.$el.find('.page-container'));

				this.pages.right = new PageView({ 
					collection: that.collection,
					sentence_resource_uri: next_uri,
					side: 'right' 
				});
				this.pages.right.render()
					.$el
					.appendTo(this.$el.find('.page-container'));
			}
			// Otherwise, turn the pages
			else {
				this.pages.left.turnToPage(CTS);
				this.pages.right.turnToPage(nextCTS);
			}
		}
	});

	return View;
});
