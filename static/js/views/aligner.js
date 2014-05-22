define(['jquery', 'underscore', 'backbone', 'collections'], function($, _, Backbone, Collections) { 

	var View = Backbone.View.extend({
		events: { },
		tagName: 'div',
		className: 'well',
		initialize: function(options) {

			var that = this;
			this.documents = new Collections.Documents();

			this.documents.on('add', this.fillDoc, this);

			this.documents.fetch();

			this.options = options;


		},
		render: function() {
			//this.$el.html("hello");
			return this;	
		},
		fillDoc: function(model) {
			if (model.get('lang') == 'grc')
				model.fetch();
		}
	});

	return View;
});
