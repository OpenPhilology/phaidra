/**
 * Corresponds to the /grammar/ endpoint in the API.
 */
define(['jquery', 
	'underscore', 
	'backbone', 
	'utils'], 
	function($, _, Backbone, Utils) {

		return Backbone.Model.extend({
			defaults: {
				'modelName': 'topic',
			},
			url: function() {
				console.log("getting url", this.get('resource_uri'));
				return this.get('resource_uri');
			},
			parse: function(response) {
				if (response && response.meta) {
					this.meta = response.meta;
				}

				this.set(response);
			}
		}
	);
});
