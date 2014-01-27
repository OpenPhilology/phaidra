define(['jquery', 'underscore', 'backbone', 'models', 'collections', 'views/module', 'views/login'], function($, _, Backbone, Models, Collections, ModuleView, LoginView) { 
	var Router = {};
	Router.Router = Backbone.Router.extend({
		routes: {
			"":"index",
			"login/": "login",
			"module/": "rootModule",
			"module/:mod": "showModule",
			"module/:mod/section/:sec": "showSect",
			"module/:mod/section/:sect/slide/:slide": "showSlide"
		},
		initialize: function() {
			// Create/Populate necessary models and collections
			// User model

			window.user = new Models.User();
			window.user.fetch({
				success: function() {
					console.log("success");
				}
			});
		},
		index: function() {
			console.log("Index called");
		},
		login: function() {
			if (!this.login_view)
				this.login_view = new LoginView({ el: '#loginform'}).render();
		},
		rootModule: function() {
			if (!this.module)
				this.fetchModules(3, 0);

			// For now, we assume that the user needs to go to our test module
			Backbone.history.navigate('module/3/section/0/slide/0', { trigger: true });
		},
		showModule: function(mod) {
			if (!this.module)
				this.fetchModules(3, 0);
			
			// For now, we assume that the user must go to the first slide
			Backbone.history.navigate('module/3/section/0/slide/0', { trigger: true });
		},
		showSect: function(mod, sect) {
			if (!this.module)
				this.fetchModules(3, 0);
				
			this.showSlide(3, 0, 0);
		},
		showSlide: function(mod, sect, slide) {
			if (!this.module)
				this.fetchModules(mod, sect);

			if (!this.module_view)
				this.module_view = new ModuleView({ el: '.slide', model: this.module }).render();

			this.module_view.showSlide(slide);

		},
		fetchModules: function(mod, sect) {
			// Fetch our static data, and use it to build the current module section

			mod = parseInt(mod);
			var that = this;

			$.ajax({
				url: '/static/js/data.json',
				dataType: 'text',
				async: false,
				success: function(data) {
					// Get the data we care about -- specific section of a module
					data = JSON.parse(data);
					var slide_data = data[mod]["modules"][sect]["slides"];

					var slides = new Collections.Slides();
					for (var i = 0; i < slide_data.length; i++) {
						slides.add(new Models.Module(slide_data[i]));
					}

					that.module = new Models.Module({
						title: data[mod]["title"],
						slides: slides
					});

				},
				error: function(xhr, status, error) {
					console.log(xhr, status, error);
				}
			});
		}
	});
	
	return Router;
});
