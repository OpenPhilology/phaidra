$(function() {

	Phaidra.Router = Backbone.Router.extend({
		routes: {
			"module/": "module",
			"module/:mod": "showModule",
			"module/:mod/section/:sec": "showSect",
			"module/:mod/section/:sect/slide/:slide": "showSlide"
		},
		initialize: function() {
			// Create/Populate necessary models and collections
			// User model
		},
		module: function() {
			if (!Phaidra.module)
				this.fetchModules(3, 0);

			// For now, we assume that the user needs to go to our test module
			Phaidra.app.navigate('module/3/section/0/slide/0', { trigger: true });
		},
		showModule: function(mod) {
			if (!Phaidra.module)
				this.fetchModules(3, 0);
			
			// For now, we assume that the user must go to the first slide
			Phaidra.app.navigate('module/3/section/0/slide/0', { trigger: true });
		},
		showSect: function(mod, sect) {
			if (!Phaidra.module)
				this.fetchModules(3, 0);
				
			this.showSlide(3, 0, 0);
		},
		showSlide: function(mod, sect, slide) {
			if (!Phaidra.module)
				this.fetchModules(mod, sect);

			if (!Phaidra.module_view)
				Phaidra.module_view = new Phaidra.Views.Module({ el: '.slide', model: Phaidra.module }).render();

			Phaidra.module_view.showSlide(slide);
		},
		fetchModules: function(mod, sect) {
			// Fetch our static data, and use it to build the current module section

			mod = parseInt(mod);

			$.ajax({
				url: '/static/js/data.json',
				dataType: 'text',
				async: false,
				success: function(data) {
					// Get the data we care about -- specific section of a module
					data = JSON.parse(data);
					var slide_data = data[mod]["modules"][sect]["slides"];

					var slides = new Phaidra.Collections.Slides();
					for (var i = 0; i < slide_data.length; i++) {
						slides.add(new Phaidra.Models.Module(slide_data[i]));
					}

					Phaidra.module = new Phaidra.Models.Module({
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

	Phaidra.app = new Phaidra.Router();
	Backbone.history.start({ pushState: true });
	console.log(Backbone.history.fragment);
	
	// Activate Bootstrap JS Components
	$('.sec').tooltip();
	$('.module .circle').tooltip({ container: 'body'});

	window.Phaidra = Phaidra;
});
