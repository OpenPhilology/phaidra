$(function() {

	Phaidra.Router = Backbone.Router.extend({
		routes: {
			"module/": "module",
			"module/:mod" : "showModule",
			"module/:mod/:slide" : "showSlide"
		},
		initialize: function() {
			// Create/Populate necessary models and collections
			// User model
		},
		module: function() {
			if (!Phaidra.modules)
				this.fetchModules();

			// For now, we assume that the user needs to go to our test module

			this.showModule(3);
		},
		showModule: function(mod) {
			if (!Phaidra.modules)
				this.fetchModules(mod);
			
			// For now, we assume that the user must go to the first slide

			this.showSlide(3, 0);
		},
		showSlide: function(mod, slide) {
			if (!Phaidra.modules)
				this.fetchModules(mod);

			if (!Phaidra.module_view)
				Phaidra.module_view = new Phaidra.Views.Module({ el: '.slide', model: Phaidra.modules.models[mod] }).render();

			Phaidra.module_view.showSlide(slide);

		},
		fetchModules: function(mod) {

			// Populate the modules/slides collections only if user is in lesson section 

			// These will be replaced with dynamic versions
			var slides = [];

			slides.push(new Phaidra.Models.Slide({ 
				includeHTML: '/static/raw/thuc/en/3.0.html',
				type: 'slide_info'
			}));
			slides.push(new Phaidra.Models.Slide({ 
				includeHTML: '/static/raw/thuc/en/3.1.1.html',
				type: 'slide_info'
			}));
			slides.push(new Phaidra.Models.Slide({ 
				includeHTML: '/static/raw/thuc/en/3.1.2.html',
				type: 'slide_info'
			}));

			Phaidra.modules =  new Phaidra.Collections.Modules([
				{
					title: 'The Greek Alphabet'
				},
				{
					title: 'Greek Diacritics'
				},
				{
					title: 'Introduction to Nouns'
				},
				{
					title: 'Introduction to Nouns',
					slides: [new Phaidra.Collections.Slides(slides)],
					levels: slides.length
				},
				{
					title: 'Introduction to Verbs'
				}
			]);
		}
	});

	Phaidra.app = new Phaidra.Router();
	Backbone.history.start({ pushState: true });
	console.log(Backbone.history.fragment);
	
	$('.sec').tooltip();
	$('.module .circle').tooltip({ container: 'body'});

	window.Phaidra = Phaidra;
});
