define(['jquery', 'underscore', 'backbone', 'models', 'collections', 'views/module', 'views/login', 'views/index'], function($, _, Backbone, Models, Collections, ModuleView, LoginView, IndexView) { 
	var Router = {};
	Router.Router = Backbone.Router.extend({
		routes: {
			"":"index",
			"login/": "login",
			"module/": "rootModule",
			"module/:mod": "showModule",
			"module/:mod/section/:sec": "showSection",
			"module/:mod/section/:sect/slide/:slide": "showSlide"
		},
		initialize: function() {
			// Create/Populate necessary models and collections
			// User model

			window.user = new Models.User();
			window.user.fetch({
				success: function() {
				},
				error: function() {
					//$('#user-info').html('Would you like to <a href="/login/">log in</a>?');
				}
			});
		},
		index: function() {
			
			if (!this.index_view)
				this.index_view = new IndexView({ el: '.main' }).render();

		},
		login: function() {
			if (!this.login_view)
				this.login_view = new LoginView({ el: '#loginform'}).render();
		},
		rootModule: function() {

			// For now, we assume that the user needs to go to our test module
			Backbone.history.navigate('module/3/section/0/slide/0', { trigger: true });
		},
		showModule: function(mod) {
			
			// For now, we assume that the user must go to the first slide
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
