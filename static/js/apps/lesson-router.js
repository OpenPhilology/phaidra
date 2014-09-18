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
			"module/:mod/section/:sec/slide/:slide": "showSlide"
		},
		// Lesson Routes
		showLessons: function() {
			if (!this.lesson_view) {
				this.lesson_view = new LessonView({ el: '#main' })
					.render();
			}
		},
		showModule: function(mod) {
			this.showSlide(mod, 0, 0);
		},
		showSection: function(mod, sect) {
			this.showSlide(mod, sect, 0);
		},
		showSlide: function(mod, sect, slide) {
			if (!this.module_view)
				this.module_view = new ModuleView({ el: $('.slide'), module: mod, section: sect, slide: slide }).render();

			// Select current slide
			this.module_view.routerNavigate(slide);
		}
	});
	
	return Router;
});
