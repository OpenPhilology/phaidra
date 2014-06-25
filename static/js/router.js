define(['jquery', 'underscore', 'backbone', 'models', 'collections', 'views/module', 
		'views/login', 'views/index', 'views/home', 'views/reader', 'views/grammar', 'views/aligner'], 
		function($, _, Backbone, Models, Collections, ModuleView, 
		LoginView, IndexView, HomeView, ReaderView, GrammarView, AlignerView) { 

	var Router = {};
	Router.Router = Backbone.Router.extend({
		routes: {
			"": "index",

			// Form handles login page
			"login/": "showLogin",

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

			// javascript function for api logout and redirect
			$("#logout-link").click(function(e) {
				e.preventDefault();
				var data = {
					"format" : "json"
				};
				$.ajax({
					url: '/api/v1/user/logout/',
					type: 'GET',
					data: data,
					contentType: 'application/json; charset=utf-8', 
					success: function(response_text) {
						alert("You are logging out.");
						window.location.assign("/home/");	
					},
					error: function(response_text) {
						alert(response_text);
					}
				});
			});
		},
		index: function() {
			if (!this.index_view) {
				this.index_view = new IndexView({ el: '.container' }).render();
			}
		},

		// Form handles login page 
		showLogin: function() {
			if (!this.login_view) {
				this.login_view = new LoginView({ el: '#loginform'})
					.render();
			}
		},

		// Creator View (Annotations/Micropubs)
		createAnnotation: function(type, CTS) {
			/*if (!this.aligner)
				this.aligner = new AlignerView({
					CTS: CTS
				});
				$('#main').html(this.aligner.render()
					.$el);*/
		},
		showCreator: function() {
			/*if (!this.aligner)
				this.createAnnotation();*/
		},

		// Traditional Grammar View
		showGrammar: function(smyth) {
			if (!this.grammar_view) {
				this.grammar_view = new GrammarView({ el: '#main', smyth: smyth})
					.render()
					.$el
					.appendTo($('#main'));
			}
		},

		// Reader Routes
		showReader: function() {
			this.updateReader(undefined);
		},
		updateReader: function(CTS) {
			if (!this.reader_view) {
				this.reader_view = new ReaderView({ 
					el: '#reader', 
					CTS: CTS 
				}).render();
			}
			else {
				this.reader_view.turnToPage(CTS);
			}
		},

		// Lesson Routes
		showLessons: function() {
			if (!this.index_view) {
				this.index_view = new IndexView({ el: '#main' })
					.render();
			}
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
