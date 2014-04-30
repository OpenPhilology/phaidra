define(['jquery', 'underscore', 'backbone', 'collections', 'views/page', 'views/notes'], function($, _, Backbone, Collections, PageView, NotesView) { 

	var View = Backbone.View.extend({
		events: { },
		initialize: function() {
			var that = this;

			// Create an empty collection of words, so views can update based on changes to it
			this.words = new Collections.Words();

			// Start by rendering the two pages
			if (!this.pages) {
				this.pages = {};
				this.pages.left = new PageView({ 
					collection: that.words, 
					side: 'right' 
				}).render()
					.$el
					.appendTo(this.$el.find('.page-container'));

				/*this.pages.right = new PageView({ 
					collection: that.words,
					side: 'right' 
				}).render()
					.$el
					.appendTo(this.$el.find('.page-container'));*/
			}

			// Render the notes viewer at the bottom of the screen
			if (!this.notes) {
				this.notes = new NotesView({
					collection: that.words
				}).render()
					.$el
					.appendTo(this.$el.find('.notes-container'));
			}

			// TODO: Make work-level progress visible 
		},
		render: function() {
			return this;	
		},
		turnToPage: function(cts) {

		}
	});

	return View;
});
