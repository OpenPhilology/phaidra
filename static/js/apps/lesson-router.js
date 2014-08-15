define(['jquery', 'underscore', 'backbone', 'models', 'collections', 'views/module', 'views/lessons'], 
		function($, _, Backbone, Models, Collections, ModuleView, LessonView) { 

	var Router = {};
	Router.Router = Backbone.Router.extend({
		routes: {
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
		// Lesson Routes
		showLessons: function() {
			if (!this.lesson_view) {
				this.lesson_view = new LessonView({ el: '#main' })
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
