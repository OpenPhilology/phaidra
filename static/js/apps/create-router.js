define(['jquery', 'underscore', 'backbone', 'views/create/create-index'], function($, _, Backbone,  CreateIndex) { 

	return Backbone.Router.extend({
		routes: {
		},
		initialize: function() {
			var index = new CreateIndex({
				el: '#main'
			});
			index.render();
		}
	});

});
