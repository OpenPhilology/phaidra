define(['jquery', 'underscore', 'backbone', 'utils'], function($, _, Backbone, Utils) {

	return Backbone.Model.extend({
		defaults: {
			'modelName': 'topic',
		},
		url: function() {
			return this.get('resource_uri');
		},
		parse: function(response) {
			console.log("parsing");
			if (response && response.meta) {
				this.meta = response.meta;
			}

			this.set(response);
		}
	});
});