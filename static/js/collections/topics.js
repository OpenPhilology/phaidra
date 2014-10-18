define(['jquery', 'underscore', 'backbone', 'models/topic', 'utils'], function($, _, Backbone, TopicModel, Utils) {

	return Backbone.Collection.extend({
		model: TopicModel,
		url: '/api/v1/grammar/',
		parse: function(response) {
			if (response && response.meta)
				this.meta = response.meta;

			return response.objects;
		},
		incrementUrl: function() {
			this.url = this.meta.next;
		},
		setEndpointLimit: function(limit) {
			this.url = '/api/v1/grammar/?limit=' + limit;
		}
	});

});
