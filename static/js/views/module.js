define(
	['jquery', 'underscore', 'backbone', 'jquery-ui-core', 'jquery-ui-slide', 'models', 'collections', 
		'views/slide-info', 'views/slide-multicomp', 'views/slide-directselect'], 
	function($, _, Backbone, jQueryUICore, jQueryUISlide, Models, Collections, 
		InfoSlideView, MultiCompSlideView, DirectSelectSlideView) { 

		var View = Backbone.View.extend({
			events: {
				'click .corner a': 'navigate'
			},
			initialize: function(options) {

				var that = this;

				// If we're loading this module initially, fetch lesson content
				if (!this.lesson) {
					this.lesson = new Collections.Slides([], {
						module: options.module, 
						section: options.section
					});
				}

				// Keep a handy reference to all the slides for nav purposes
				if (!this.slides) 
					this.slides = [];

				// Create a slide-type-to-view mapper
				this.map = {
					'slide_info': function(model) {
						return new InfoSlideView({
							model: model
						}).render()
							.$el
							.appendTo(that.$el.find('#lesson-content'));
					},
					'slide_multi_comp': function(model) {
						return new MultiCompSlideView({
							model: model
						}).render()
							.$el
							.appendTo(that.$el.find('#lesson-content'));
					},
					'slide_treebank': function(model) {
						return new TreebankingView({
							model: model
						}).render()
							.$el
							.appendTo(that.$el.find('#lesson-content'));
					},
					'slide_direct_select': function(model) {
						return new DirectSelectSlideView({
							model: model
						}).render()
							.$el
							.appendTo(that.$el.find('#lesson-content'));
					}
				};

				this.lesson.bind('add', _.bind(this.addSlide, this));
				this.lesson.populate();
				this.$el.find('.lesson-header h1').html(this.lesson.meta('moduleTitle'));
				this.$el.find('.lesson-header h2').html(this.lesson.meta('sectionTitle'));
				
			},
			addSlide: function(model, collection, options) {
				var selector = '#' + model.get('type');
				var that = this;

				// Set for easy navigation to next slide
				model.set('index', model.collection.indexOf(model));

				// The Module view keeps references to the various slide views
				var view = this.map[model.attributes.type](model);
				this.slides.push(view);

				// Create a progress bar section for each slide
				if (model.get('index') < model.collection.meta('initLength') - 1) {
					var progress = this.$el.find('.lesson-progress');
					progWidth = (100 / (model.collection.meta('initLength') - 1)); 
					progress.append('<div class="bar" style="width: ' + progWidth + '%"></div>');
				}
			},
			render: function() {
				return this;	
			},
			showSlide: function(slide) {
				slide = parseInt(slide);

				// Show the correct slide view
				for (var i = 0; i < this.slides.length; i++) {
					this.slides[i].hide();
				}
				this.slides[slide].show('slide', { direction: 'right' }, 500, function() {
					// Trigger resize for formerly hidden elements
					window.dispatchEvent(new Event('resize'));
				});

				this.recordTimestamp(slide);
				this.updateProgress(slide);
				this.updateNavigation(slide);
			},
			// Update the navigation link
			updateNavigation: function(slide) {
				if (!this.slides[slide + 1])
					this.$el.find('.corner a').hide();
				else {
					var url = '/' + Backbone.history.fragment.split('/').splice(0, 5).join('/') + '/' + (1 + slide);
					this.$el.find('.corner a').attr('href', url);
				}
			},
			// Record the time that the user started viewing the slide
			recordTimestamp: function(slide) {
				this.slides[slide].data('startTime', new Date());
			},
			// Display proper progress to the user
			updateProgress: function(slide) {
				var progress = this.$el.find('.lesson-progress').children();
				for (var i = 0; i < progress.length; i++) {
					if (i < slide)
						$(progress[i]).addClass('complete');	
					else
						$(progress[i]).removeClass('complete');
				}
			},
			navigate: function(e) {
				e.preventDefault();

				var url = $(e.target).attr('href');
				Backbone.history.navigate(url, { trigger: true });
			}
		});

	return View;
});
