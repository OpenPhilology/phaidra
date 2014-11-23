define(['jquery', 'underscore', 'backbone', 'models/topic', 'utils'], function($, _, Backbone, TopicModel, Utils) {

	return Backbone.Collection.extend({
		model: TopicModel,
		url: '/api/v1/grammar/',
		parse: function(response) {
			if (response && response.meta)
				this.meta = response.meta;

			return response.objects;
		},
		initialize: function() {
			_.bindAll(this, 'handleAccuracySuccess');
			_.bindAll(this, 'handleAccuracyError');
		},
		incrementUrl: function() {
			this.url = this.meta.next;
		},
		setEndpointLimit: function(limit) {
			this.url = '/api/v1/grammar/?limit=' + limit;
		},
		getAccuracies: function(options) {
			var that = this;

			$.ajax({
				url: '/api/v1/visualization/least_accurate',
				type: 'GET',
				headers: { 'X-CSRFToken': window.csrf_token },
				contentType: 'application/json',
				success: function(response) {
					that.handleAccuracySuccess(response, options.success);
				},
				error: function(response) {
					that.handleAccuracyError(response, options.error);
				}
			});
		},
		handleAccuracySuccess: function(response, callback) {

			// Merge in accuracies in to existing collection
			response.accuracy_ranking.forEach(function(ranking) {
				this.findWhere({ ref: ranking.ref }).set('average', ranking.average);
			}.bind(this));

			callback();
		},
		handleAccuracyError: function(response, callback) {
			console.log(response);
			callback();
		}
	});
});
