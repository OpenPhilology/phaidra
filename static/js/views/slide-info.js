define(['jquery', 'underscore', 'backbone', 'models', 'collections', 'text!/templates/js/slide-info.html', 'daphne', 'morea'], function($, _, Backbone, Models, Collections, Template, Daphne, Morea) {
	var View = Backbone.View.extend({
		tagName: 'div',
		className: 'slide-unit',
		template: _.template(Template),
		events: { },
		initialize: function(options) {
			this.options = options;
		},
		render: function() {
			this.$el.html(this.template(this.model.attributes));
			this.$el.find('a[data-toggle="popover"]').popover();
			this.$el.find('em[data-toggle="tooltip"]').tooltip();

			// If there are any parse trees, render them
			// TODO: Make this more robust
			this.$el.find('[data-toggle="daphne"]').each(function(i, el) {
				var words = JSON.parse(el.innerHTML);
				el.innerHTML = '';

				new Daphne(el, {
					data: words,
					mode: el.getAttribute('data-mode'),
					width: el.getAttribute('data-width') || 200,
					height: 400,
					initialScale: 0.9
				});
			});

			this.$el.find('[data-toggle="morea"]').each(function(i, el) {
				new Morea(el, {
					mode: el.getAttribute('data-mode'),
					dataUrl: el.getAttribute('data-dataUrl'),
					targets: el.getAttribute('data-targets').split(","),
					langs: {
						"grc": {
							"hr": "Greek",
							"resource_uri": "",
							"dir": "ltr"
						},
						"en": {
							"hr": "English",
							"resource_uri": "",
							"dir": "ltr"
						}
					}
				});
			});

			return this;
		},
		navigate: function(e) {
			e.preventDefault();

			// Try not to laugh -- this will be fixed
			//var url = Backbone.history.fragment.split('/').splice(0, 5).join('/') + '/' + (this.model.get('index') + 1);

			//Backbone.history.navigate(url, { trigger: true });
		}
	});

	return View;
});
