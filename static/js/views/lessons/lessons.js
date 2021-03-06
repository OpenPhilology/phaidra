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
				'click a.module': 'navigate'
			},
			initialize: function(options) {
				_.bindAll(this, 'checkScroll');
				_.bindAll(this, 'renderTopics');

				$(window).scroll(this.checkScroll);

				this.user = options.user;
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
					success: function(models) {
						that.collection.getAccuracies({ success: that.renderTopics });	
					}
				});
			},
			renderTopics: function(topicCollection) {
				var template = _.template(LessonListTemplate);
				this.$el.append(template({
					topics: this.collection.models, 
					LOCALE: LOCALE, 
					user: this.user 
				})); 
				this.isLoading = false;
			},
			checkScroll: function() {
				var triggerPoint = 100;
				if (!this.isLoading && (this.el.scrollTop + this.el.clientHeight + triggerPoint > this.el.scrollHeight)) {
					this.collection.incrementUrl();
					this.loadTopics();
				}
			},
			navigate: function(e) {

				// If they clicked outside the anchor, adjust target
				if (e.target.tagName === 'IMG' || e.target.tagName === 'P') 
					e.target = e.target.parentElement;

				// Make the link follow-through 
				if (e.target.classList.indexOf('admin') !== -1) {
					e.preventDefault();
					this.router.navigate(e.target.getAttribute('href'), { trigger: true });
				}
			}
		});
	}
);
