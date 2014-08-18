define(
	['jquery', 'underscore', 'backbone', 'jquery-ui-core', 'jquery-ui-slide', 'models', 'collections', 
		'views/slide-info', 'views/slide-multicomp', 'views/slide-directselect', 'views/slide-last', 'utils'], 
	function($, _, Backbone, jQueryUICore, jQueryUISlide, Models, Collections, 
		InfoSlideView, MultiCompSlideView, DirectSelectSlideView, LastSlideView, Utils) { 

		var View = Backbone.View.extend({
			events: {
				'click .corner.right a': 'navigate'
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
							model: model,
							collection: that.lesson
						}).render()
							.$el
							.appendTo(that.$el.find('#lesson-content'));
					},
					'slide_last': function(model) {
						return new LastSlideView({
							model: model,
							collection: that.lesson
						}).render()
							.$el
							.appendTo(that.$el.find('#lesson-content'));
					},
					'slide_multi_comp': function(model) {
						return new MultiCompSlideView({
							model: model,
							collection: that.lesson
						}).render()
							.$el
							.appendTo(that.$el.find('#lesson-content'));
					},
					'slide_treebank': function(model) {
						return new TreebankingView({
							model: model,
							collection: that.lesson
						}).render()
							.$el
							.appendTo(that.$el.find('#lesson-content'));
					},
					'slide_direct_select': function(model) {
						return new DirectSelectSlideView({
							model: model,
							collection: that.lesson
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
				model.set('index', this.lesson.indexOf(model));

				// The Module view keeps references to the various slide views
				var view = this.map[model.get('type')](model);
				this.slides.push(view);

				// Create a progress bar section for each slide
				var progress = this.$el.find('.lesson-progress');
				progWidth = (100 / (this.lesson.meta('initLength') - 1)); 

				// Since we add in slides async, this needs to automatically adjust
				var sections = progress.find('.bar');
				for (var i = 0; i < sections.length; i++) {
					sections[i].style.width = progWidth + '%';
				}
				while (sections.length < (this.lesson.meta('initLength') -1)) {
					progress.append('<div class="bar" style="width: ' + progWidth + '%"></div>');
					sections = progress.find('.bar');
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
				// Trigger delayed rendering if needed
				this.lesson.at(slide).delayedRender();

				if (this.slides[slide]) {
					this.slides[slide].show('slide', { direction: 'right' }, 500, function() {
						// Trigger resize for formerly hidden elements
						window.dispatchEvent(new Event('resize'));
					});

					this.recordTimestamp(slide);
					this.updateProgress(slide);

					if (this.lesson.at(1 + slide))
						this.lesson.at(1 + slide).delayedRender();
				}
				else {
					this.$el.html("<h1>Looks like you overshot!</h1><a href=\"/lessons\">Return to Lessons</a>");
				}

				this.updateNavigation(slide);
			},
			// Update the navigation link
			updateNavigation: function(slide) {

				var frag = Backbone.history.fragment.split('/');

				if (!this.slides[slide + 1]) {
					// Add in the summary slide
					if (this.lesson.meta('initLength') === slide + 1) {
						this.lesson.add({ type: "slide_last" }, { at: (1 + slide)});
					}
					// Let them continue to the next unit
					else {
						this.lesson.trigger('completed');
						frag = Backbone.history.fragment.split('/');
						var mod = parseInt(frag[1]), section = parseInt(frag[3]);
						if (Utils.Content[mod].modules[section + 1]) {
							frag[3] = (parseInt(frag[3]) + 1).toString();
						}
						else {
							frag[3] = "0";
							frag[1] = (parseInt(frag[1]) + 1).toString();
						}
						slide = -1;
						this.undelegateEvents();		
					}
				}
				// Otherwise, simply proceed to next slide
				url = '/' + frag.splice(0, 5).join('/') + '/' + (1 + slide);
				this.$el.find('.corner a').attr('href', url);
				this.$el.find('a[title="Continue"]').attr('href', url);
			},
			// Record the time that the user started viewing the slide
			recordTimestamp: function(slide) {
				this.slides[slide].data('starttime', new Date());
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
