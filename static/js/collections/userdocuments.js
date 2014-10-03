define(['jquery', 'underscore', 'backbone', 'models/userdocument', 'utils'], function($, _, Backbone, UserDocumentModel, Utils) {

	return Backbone.Collection.extend ({ 
		model: UserDocumentModel,
		url: '/api/v1/user_document/',
		parse: function(response) {
			
			// Flatten our references to sentence URIs
			for (var i = 0; i < response.objects.length; i++) {
				response.objects[i].sentences = response.objects[i].sentences.map(function(el) {
					return el.resource_uri;
				});
			}
			this.add(response.objects);
		}
	});

});
