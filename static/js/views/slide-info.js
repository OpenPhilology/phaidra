define(['jquery', 'underscore', 'backbone', 'models', 'collections', 'text!templates/slide-info.html'], function($, _, Backbone, Models, Collections, Template) {
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
