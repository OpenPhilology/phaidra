define(['jquery', 'underscore', 'backbone', 'models', 'collections', 'views/module', 'views/login', 'views/index', 'views/reader', 'views/grammar'], function($, _, Backbone, Models, Collections, ModuleView, LoginView, IndexView, ReaderView, GrammarView) { 
	var Router = {};
	Router.Router = Backbone.Router.extend({
		routes: {
			"": "index",

			// Form handles login page
			"login/": "login",

			// Traditional Grammar Routes
			"grammar/:smyth": "showGrammar",

			// Reader Routes
			"reader/:cts": "updateReader",
			"reader/": "showReader",

			// Create (Annotate/Micropub Routes)
			"create/:type/:cts": "createAnnotation",
			"create/": "showCreator",

			// Lesson Routes
			"lessons/":"showLessons",
			"module/": "forwardModule",
			"module/:mod": "showModule",
			"module/:mod/section/:sec": "showSection",
			"module/:mod/section/:sect/slide/:slide": "showSlide"
		},
		initialize: function() {
			// Create/Populate necessary models and collections
		},
		index: function() {
			// TODO: Move this into its own view, along with reg. form handling
			$('#greeting-text a').on('click', function(e) {
				e.preventDefault();
				$('#greeting-text').slideUp('slow', function() {
					$('#register-text').slideDown('slow');
				});
			});
		},

		// Form handles login page 
		showLogin: function() {
			if (!this.login_view)
				this.login_view = new LoginView({ el: '#loginform'}).render();
		},

		// Creator View (Annotations/Micropubs)
		createAnnotation: function(type, cts) {

		},
		showCreator: function() {

		},

		// Traditional Grammar View
		showGrammar: function(smyth) {
			if (!this.grammar_view)
				this.grammar_view = new GrammarView({ el: '#main', smyth: smyth}).render().$el.appendTo($('#main'));
		},

		// Reader Routes
		showReader: function() {
			if (!this.reader_view)
				this.reader_view = new ReaderView({ el: '#reader' }).render();

			this.updateReader(undefined);
		},
		updateReader: function(cts) {
			if (!this.reader_view)
				this.showReader();

			this.reader_view.turnToPage(cts);
		},

		// Lesson Routes
		showLessons: function() {
			if (!this.index_view)
				this.index_view = new IndexView({ el: '#main' }).render();
		},
		forwardModule: function() {
			Backbone.history.navigate('module/3/section/0/slide/0', { trigger: true });
		},
		showModule: function(mod) {
			Backbone.history.navigate('module/3/section/0/slide/0', { trigger: true });
		},
		showSection: function(mod, sect) {
			this.showSlide(3, 0, 0);
		},
		showSlide: function(mod, sect, slide) {
			if (!this.module_view)
				this.module_view = new ModuleView({ el: $('.slide'), module: mod, section: sect }).render();

			this.module_view.showSlide(slide);
		}
	});
	
	return Router;
});
