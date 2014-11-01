/**
 * LESSON ROUTER
 * Deals with navigation between the lesson screen and the selected microlesson.
 */ 
define(['jquery', 
	'underscore', 
	'backbone', 
	'models/user',
	'collections/topics', 
	'views/lessons/lessons', 
	'views/lessons/microlesson'], 
	function($, _, Backbone, UserModel, TopicsCollection, LessonListView, MicrolessonView) { 

		return Backbone.Router.extend({
			initialize: function(options) {
				
				var that = this;

				// Topics Collection used by both Lesson and Microlesson Views
				this.topicsCollection = new TopicsCollection();
				this.user = new UserModel();

				// Defer routing until our collections are fetched
				var complete = _.invoke([that.topicsCollection, that.user], 'fetch');

				// Then assign routes and trigger routing
				$.when.apply($, complete).done(function() {

					that.route(/^(.*?)\/lessons\/(.*?)$/, 'showLessons');
					that.route(/^(.*?)\/lessons\/(.+)$/, 'showMicrolesson');
					Backbone.history.start({ pushState: true });

				}.bind(this));
			},
			showLessons: function(lang) {
				this.hideMicrolesson();

				if (!this.lessonListView) {
					this.lessonListView = new LessonListView({ 
						collection: this.topicsCollection, 
						user: this.user,
						router: this
					}).render();
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
					this.microlessonView = new MicrolessonView({ 
						el: '#main', 
						collection: this.topicsCollection, 
						index: id, 
						user: this.user
					});
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
