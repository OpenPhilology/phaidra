define(['jquery', 'underscore', 'backbone', 'models/document', 'utils'], function($, _, Backbone, DocumentModel, Utils) {

	return Backbone.Collection.extend({
		model: DocumentModel,
		url: '/api/v1/document/',
		parse: function(response) {

			// Flatten our references to sentence URIs
			for (var i = 0; i < response.objects.length; i++) {
				response.objects[i].sentences = response.objects[i].sentences.map(function(el) {
					return el.resource_uri;
				});
			}
			var docs = this.calcCompletion(response.objects);
			this.add(docs);
		},
		calcCompletion: function(docs) {
			docs.forEach(function(m) {
				// Use CTS to group
				var work = m.CTS.split(':')[3].split('.');
				var common = work[0] + work[1];
				m.family = common;
			});
			docs.forEach(function(m) {
				var orig = docs.filter(function(model) {
					return model.common === m.common && model.lang === 'grc';
				})[0];

				m.completion = (m.sentences.length / orig.sentences.length) * 100;

			}.bind(this));
			
			return docs;
		}
	});

});
