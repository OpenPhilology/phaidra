define(['jquery', 
	'underscore', 
	'backbone', 
	'utils', 
	'text!/templates/js/lessons/lesson_list.html'], 
	function($, _, Backbone, Utils, LessonListTemplate) { 

		return Backbone.View.extend({
			tagName: 'div',
			className: 'row',
			events: { 
				'click .module': 'navigate'
			},
			initialize: function(options) {
				_.bindAll(this, 'checkScroll');
				$(window).scroll(this.checkScroll);

				this.isLoading = false;
				this.router = options.router;
			},
			render: function() {
				this.loadTopics();	
				return this;	
			},
			loadTopics: function() {
				var that = this;

				this.isLoading = true;
				this.collection.fetch({
					success: function(topics) {
						var template = _.template(LessonListTemplate);
						that.$el.append(template({ topics: topics.models, LOCALE: LOCALE })); 
						that.isLoading = false;
					}
				});
			},
			checkScroll: function() {
				var triggerPoint = 100;
				if (!this.isLoading && (this.el.scrollTop + this.el.clientHeight + triggerPoint > this.el.scrollHeight)) {
					this.collection.incrementUrl();
					this.loadTopics();
				}
			},
			navigate: function(e) {
				e.preventDefault();

				// If they clicked outside the anchor, adjust target
				if (e.target.tagName === 'DIV') 
					e.target = e.target.parentElement;

				this.router.navigate(e.target.getAttribute('href'), { trigger: true });
			}
		});
	}
);
