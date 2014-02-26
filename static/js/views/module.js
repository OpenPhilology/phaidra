define(
	['jquery', 'underscore', 'backbone', 'models', 'collections', 'views/slide_info', 'views/slide_multi_composition','views/FrankTestView','views/SimpleVocabView', 'views/slide_direct_select'], 
	function($, _, Backbone, Models, Collections, InfoSlideView, MultiCompSlideView, FrankTestView, SimpleVocabView, DirectSelectSlideView) { 

		var View = Backbone.View.extend({
			events: {
				'click .lesson-right-menu a': 'navigate'
			},
			initialize: function(options) {

				/*
					If model doesn't exist, it can go build itself.
				*/
				if (!this.lesson) {
					console.log("creating a new lesson");
					this.lesson = new Collections.Slides([], {
						module: options.module, 
						section: options.section
					});
				}
				
				if (!this.slides) this.slides = [];

				this.lesson.bind('add', _.bind(this.addSlide, this));
				this.lesson.populate();
				
			},
			addSlide: function(model, collection, options) {
				var selector = '#' + model.get('type');
				var that = this;
				var view;

				// Set for easy navigation to next slide
				model.set('index', model.collection.indexOf(model));

				// Decide which type of view to create
				if (selector == '#slide_multi_composition') {
					view = new MultiCompSlideView({ 
						model: model, 
						template: _.template(this.$el.find('#slide_multi_composition').html()) 
					}).render()
						.$el
						.appendTo(this.$el.find('#lesson-content'));
				}
				else if (selector == '#slide_info') {
					view = new InfoSlideView({ 
						model: model, 
						template: _.template(this.$el.find('#slide_info').html()) 
					}).render()
						.$el
						.appendTo(this.$el.find('#lesson-content'));
				}
				else if (selector == '#slide_direct_select') {
					view = new DirectSelectSlideView({ 
						model: model, 
						template: _.template(this.$el.find('#slide_direct_select').html()) 
					}).render()
						.$el
						.appendTo(this.$el.find('#lesson-content'));
				}

				// The Module view keeps references to the various slide views
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

				console.log("show slide called for ", slide);
				console.log("views so far", _(this.slides).clone());

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
