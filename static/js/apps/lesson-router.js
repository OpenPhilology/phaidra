/**
 * LESSON ROUTER
 * Deals with navigation between the lesson screen and the selected microlesson.
 */ 
define(['jquery', 
	'underscore', 
	'backbone', 
	'collections/topics', 
	'views/lessons/lessons', 
	'views/lessons/microlesson'], 
	function($, _, Backbone, TopicsCollection, LessonListView, MicrolessonView) { 

		return Backbone.Router.extend({
			initialize: function(options) {
				this.route(/^(.*?)\/lessons\/(.*?)$/, 'showLessons');
				this.route(/^(.*?)\/lessons\/(.+)$/, 'showMicrolesson');

				// Topics Collection used by both Lesson and Microlesson Views
				this.topicsCollection = new TopicsCollection();
			},
			showLessons: function(lang) {
				this.hideMicrolesson();

				if (!this.lessonListView) {
					this.lessonListView = new LessonListView({ collection: this.topicsCollection, router: this }).render();
					$('#main .module-container').append(this.lessonListView.el);
				}
				else {
					this.lessonListView.$el.show();
				}
			},
			hideLessons: function() {
				if (this.lessonListView) 
					this.lessonListView.$el.hide();
			},
			showMicrolesson: function(lang, index) {
				this.hideLessons();
				var id = parseInt(index);

				if (!this.microlessonView)
					this.microlessonView = new MicrolessonView({ el: '#main', index: id, collection: this.topicsCollection });
				if (this.microlessonView.options.index !== id) {
					this.microlessonView.initialize({ index: id });
				}
			},
			hideMicrolesson: function() {
				if (this.microlessonView)
					this.microLessonView.$el.hide();
			}
		});
	}
);
