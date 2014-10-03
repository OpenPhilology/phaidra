define(['jquery', 'underscore', 'backbone', 'utils'], function($, _, Backbone, Utils) {
	var User = {};

	User = Backbone.Model.extend({
		defaults: {
			'modelName': 'user',
		},
		url: '/api/v1/user/',
		parse: function(response) {
			if (response && response.meta)
				this.meta = response.meta;
			this.set(response.objects.filter(function(obj) {
				return obj.username === U;
			})[0]);
			this.set("locale", locale);
			this.set("language", locale.split('-')[0]);
		}
	});

	return User;

});
