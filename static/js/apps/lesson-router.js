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
				this.module_view = new ModuleView({ el: $('.slide'), module: mod, section: sect, slide: slide }).render();

			this.module_view.setCurrentSlide(slide);
		}
	});
	
	return Router;
});
