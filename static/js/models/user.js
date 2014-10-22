define(['jquery', 'underscore', 'backbone', 'utils'], function($, _, Backbone, Utils) {
	return Backbone.Model.extend({
		defaults: {
			'modelName': 'user',
		},
		url: '/api/v1/user/',
		parse: function(response) {
			this.set(response);
		}
	});
});
