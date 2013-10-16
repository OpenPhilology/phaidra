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
				this.fetchModules();
			
			// For now, we assume that the user must go to the first slide

			this.showSlide(3, 0);
		},
		showSlide: function(mod, slide) {
			if (!Phaidra.modules)
				this.fetchModules();

			// Render the HTML for modules
			Phaidra.module_view = new Phaidra.Views.Module({ el: '.slide', model: Phaidra.modules.models[mod] }).render();
			Phaidra.module_view.showSlide(slide);

		},
		fetchModules: function() {
			// Populate the modules/slides collections only if user is in lesson section 

			// These will be replaced with dynamic versions

			var alphaDecSlides = new Phaidra.Collections.Slides([
				{
					title: 'Intro',
					content: 'just stuff',
					type: 'slide_info'
				},
				{
					title: 'Feminines in -&eta;',
					content: 'What is the nominative singular form for "The Fine Tent"?',
					type: 'slide_multi_composition',
					options: [
						[{
							display: 'ἡ',
							value: 'ἡ'
						},
						{
							display: 'τῆς',
							value: 'τῆς`'
						}],
						[{
							display: 'καλαῖς',
							value: 'καλαῖς'
						},
						{
							display: 'καλὴ',
							value: 'καλὴ'
						}],
						[{
							display: 'σκηνῆς',
							value: 'σκηνῆς'
						},
						{
							display: 'σκηνή',
							value: 'σκηνή'
						}]
					]
				},
				{
					title: 'Other',
					content: 'second content',
					type: 'slide_multi_composition',
					options: [
						[{
							display: 'choice',
							value: 'choice'
						}]
					]
				},
			]);

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
					title: 'Alpha Declension - Feminines in &eta;',
					slides: alphaDecSlides,
					levels: alphaDecSlides.length
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
