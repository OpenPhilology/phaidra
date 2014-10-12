define(['jquery', 'underscore', 'backbone', 'utils', 'collections/topics', 'text!/templates/js/lessons/lesson_list.html'], function($, _, Backbone, Utils, TopicsCollection, LessonListTemplate) { 

	return Backbone.View.extend({
		tagName: 'div',
		className: 'row',
		events: { },
		initialize: function() {
			_.bindAll(this, 'checkScroll');
			$(window).scroll(this.checkScroll);

			this.isLoading = false;
			this.topicsCollection = new TopicsCollection();
		},
		render: function() {
			this.loadTopics();	
			return this;	
		},
		loadTopics: function() {
			var that = this;

			this.isLoading = true;
			this.topicsCollection.fetch({
				success: function(topics) {
					var template = _.template(LessonListTemplate);
					that.$el.append(template({ topics: topics.models })); 
					that.isLoading = false;
				}
			});
		},
		checkScroll: function() {
			var triggerPoint = 100;
			if (!this.isLoading && (this.el.scrollTop + this.el.clientHeight + triggerPoint > this.el.scrollHeight)) {
				this.topicsCollection.incrementUrl();
				this.loadTopics();
			}
		}
	});

});
