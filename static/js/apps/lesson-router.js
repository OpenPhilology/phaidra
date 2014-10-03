/**
 * LESSON ROUTER
 * Deals with navigation between the lesson screen and the selected microlesson.
 */ 
define(['jquery', 'underscore', 'backbone', 'views/lessons/lessons', 'views/lessons/microlesson'], function($, _, Backbone, LessonListView, MicrolessonView) { 

	return Backbone.Router.extend({
		routes: {
			"lessons/":"showLessons",
			"lessons/:s": "showMicrolesson"
		},
		showLessons: function() {
			this.hideMicrolesson();

			if (!this.lessonListView)
				this.lessonListView = new LessonListView({ el: '#main' }).render();
			else
				this.lessonListView.$el.show();
		},
		hideLessons: function() {
			if (this.lessonListView) 
				this.lessonListView.$el.hide();
		},
		showMicrolesson: function(s) {
			this.hideLessons();

			if (!this.microlessonView)
				this.microlessonView = new MicrolessonView({ el: '#main', ref: s });
			if (this.microlessonView.options.ref !== s) {
				this.microlessonView.initialize({ ref: s });
			}
		},
		hideMicrolesson: function() {
			if (this.microlessonView)
				this.microLessonView.$el.hide();
		}
	});
});
