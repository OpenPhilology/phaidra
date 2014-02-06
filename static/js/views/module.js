define(
	['jquery', 'underscore', 'backbone', 'models', 'collections', 'views/slide_info', 'views/slide_multi_composition','views/FrankTestView','views/SimpleVocabView'], 
	function($, _, Backbone, Models, Collections, InfoSlideView, MultiCompSlideView,FrankTestView,SimpleVocabView) { 

		var View = Backbone.View.extend({
			events: {
				'click .lesson-right-menu a': 'navigate'	
			},
			initialize: function() {
				this.slides = [];
			},
			render: function() {
				var that = this;
				this.$el.find('h3').html(this.model.get('title'));

				// Create as many slides as there are in this module
				var slides = this.model.get('slides');
				var progress = this.$el.find('.lesson-progress');

				var progWidth = Math.floor(100 / (slides.length - 1)) || 100;

				for (var i = 0; i < slides.length; i++) {
					var selector = '#' + slides.at(i).get('type');	
					var view;

					// Set for easy navigation to next slide
					slides.at(i).set('index', i);





					if (selector == '#slide_multi_composition') {
						view = new MultiCompSlideView({ 
							model: slides.at(i), 
							template: _.template(that.$el.find('#slide_multi_composition').html()) 
						}).render()
							.$el
							.appendTo(this.$el.find('#lesson-content'));
					}
					else


if (selector == '#slide_info') {
						view = new InfoSlideView({ 
							model: slides.at(i), 
							template: _.template(that.$el.find('#slide_info').html()) 
						}).render()
							.$el
							.appendTo(this.$el.find('#lesson-content'));
					}

else //TODO requirejs: testen ob includes als array möglich und reference by name
 if (typeof selector=='string' && selector[0]=="#" && that.$el.find(selector))
{
 //TODO bad practice using eval but atm ok


fnName = selector.substring(1);
  var selectorFunc= eval('(function(){ try {return '+fnName+'}catch(e){ return null;} })()')

if (selectorFunc==null) throw new Error(selector+" has no corresponding view defined in local r global scope")
view = new selectorFunc({ 
							model: slides.at(i), 
							template: _.template(that.$el.find(selector).html()) 
						})

.render().$el.appendTo(this.$el.find('#lesson-content'));


}


					this.slides.push(view);

					// Create a progress bar section for each slide
					if (i < (slides.length - 1))
						progress.append('<div class="bar" style="width: ' + progWidth + '%"></div>');
				}

				
				return this;	
			},
			showSlide: function(slide) {
				slide = parseInt(slide);

				// Show the correct slide
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
