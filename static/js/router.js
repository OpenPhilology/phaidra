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
					title: 'An Introduction to Cases',
					content: '<p>There are five <strong>CASES</strong> in Greek, the nominative, genitive, dative, accusative, and vocative.</p>' + 
						'<p>The nominative and vocative plural are always alike. In neuters, the nominative, accusative, and vocative are alike in all numbers; in the plural these end in α.</p>' +
						'<p>In English, readers rely on the order that words appear in a sentence to indicate the grammatical function of each word.  In Ancient Greek, their case tells the reader the grammatical function of each word in the sentence.</p>',
					type: 'slide_info'
				},
				{
					title: 'The Nominative Case',
					content: '',
					type: 'slide_info'
				},
				{
					title: 'Feminines in -&alpha;',
					content: 'What is the accusative plural form for "The Small Country"?',
					type: 'slide_multi_composition',
					options: [
						[{
							display: 'ἡ',
							value: 'ἡ'
						},
						{
							display: 'τῆς',
							value: 'τῆς`'
						}, 
						{
							display: 'τὰς',
							value: 'τὰς'
						}],
						[{
							display: 'μῑκρᾷ',
							value: 'μῑκρᾷ'
						},
						{
							display: 'μῑκρὰς',
							value: 'μῑκρὰς'
						},
						{
							display: 'μῑκρὰ',
							value: 'μῑκρὰ'
						}],
						[{
							display: 'χώρᾱς',
							value: 'χώρᾱς'
						},
						{
							display: 'χώραιν',
							value: 'χώραιν'
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
					title: 'Introduction to Nouns',
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
