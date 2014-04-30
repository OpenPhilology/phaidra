define(['jquery', 'underscore', 'backbone', 'models', 'collections', 'views/module', 'views/login', 'views/index', 'views/reader'], function($, _, Backbone, Models, Collections, ModuleView, LoginView, IndexView, ReaderView) { 
	var Router = {};
	Router.Router = Backbone.Router.extend({
		routes: {
			"": "index",
			"lessons/":"lessons",
			"login/": "login",
			"reader/": "showReader",
			"reader/:cts": "updateReader",
			"module/": "forwardModule",
			"module/:mod": "showModule",
			"module/:mod/section/:sec": "showSection",
			"module/:mod/section/:sect/slide/:slide": "showSlide"
		},
		/*
		*	Fetches data from the server about our user and their lesson progress.
		*	TODO: Store this in local storage.
		*/
		initialize: function() {
			// Create/Populate necessary models and collections
			// User model
			window.user = new Models.User();
			window.user.fetch();
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
		/*
		*	Does the visualizations visible on the main lesson screen
		*/
		displayLessons: function() {
			if (!this.index_view)
				this.index_view = new IndexView({ el: '.main' }).render();
		},
		/*
		*	Handles user login via a form
		*/
		displayLogin: function() {
			if (!this.login_view)
				this.login_view = new LoginView({ el: '#loginform'}).render();
		},
		/*
		*	Manages routing for the assisted reader	
		*/
		showReader: function() {
			if (!this.reader_view)
				this.reader_view = new ReaderView({ el: '#reader' }).render();
		},
		updateReader: function(cts) {
			if (!this.reader_view)
				this.showReader();

			this.reader_view.turnToPage(cts);
		},
		/*
		*	Router functions related to displaying the correct lesson content -- 
		*	will be replaced by sys. serving content from the backend
		*/
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
