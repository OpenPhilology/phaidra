define(
	['jquery', 'underscore', 'backbone', 'models', 'collections', 'views/slide-info', 'views/slide-multicomp', 'views/slide-directselect'], 
	function($, _, Backbone, Models, Collections, InfoSlideView, MultiCompSlideView, DirectSelectSlideView) { 

		var View = Backbone.View.extend({
			events: {
				'click .lesson-right-menu a': 'navigate'
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
					'slide_multi_comp': 'MultiCompSlideView',
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
				this.$el.find('.lesson-header h1').html(this.lesson.meta('title'));
				
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
					progWidth = Math.floor(100 / (model.collection.meta('initLength') - 1));
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
				this.slides[slide].show();

				// Display proper progress to the user
				var progress = this.$el.find('.lesson-progress').children();
				for (var i = 0; i < progress.length; i++) {
					if (i < slide)
						$(progress[i]).addClass('complete');	
					else
						$(progress[i]).removeClass('complete');
				}

				// Update the navigation link
				if (!this.slides[slide + 1])
					this.$el.find('.lesson-right-menu a').hide();
				else {
					var url = '/' + Backbone.history.fragment.split('/').splice(0, 5).join('/') + '/' + (1 + slide);
					this.$el.find('.lesson-right-menu a').attr('href', url);
				}
			},
			navigate: function(e) {
				e.preventDefault();

				var url = $(e.target).parent().attr('href');
				Backbone.history.navigate(url, { trigger: true });
			}
		});

	return View;
});
