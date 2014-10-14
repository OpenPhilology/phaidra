/**
 * LESSON ROUTER
 * Deals with navigation between the lesson screen and the selected microlesson.
 */ 
define(['jquery', 'underscore', 'backbone', 'views/lessons/lessons', 'views/lessons/microlesson'], function($, _, Backbone, LessonListView, MicrolessonView) { 

	return Backbone.Router.extend({
		initialize: function(options) {
			this.route(/^(.*?)\/lessons\/(.*?)$/, 'showLessons');
			this.route(/^(.*?)\/lessons\/(.+)$/, 'showMicrolesson');
		},
		showLessons: function(lang) {
			this.hideMicrolesson();

			if (!this.lessonListView) {
				this.lessonListView = new LessonListView().render();
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
		showMicrolesson: function(lang, s) {
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
