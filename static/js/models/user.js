define(['jquery', 'underscore', 'backbone', 'utils'], function($, _, Backbone, Utils) {
	return Backbone.Model.extend({
		defaults: {
			'modelName': 'user',
		},
		urlRoot: '/api/v1/user/',
		parse: function(response) {
			this.set(response);
		}
	});
});
