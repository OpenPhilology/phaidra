define(['jquery', 'underscore', 'backbone', 'models', 'collections', 'views/create-index'], function($, _, Backbone, Models, Collections, CreateIndex) { 

	var Router = {};
	Router.Router = Backbone.Router.extend({
		routes: {
		},
		initialize: function() {
			// Create/Populate necessary models and collections
			this.documents = new Collections.Documents();
			this.documents.bind('add', this.index, this);
			this.documents.fetch();

			// javascript function for api logout and redirect
			$("#logout-link").click(function(e) {
				e.preventDefault();
				var data = {
					"format" : "json"
				};
				$.ajax({
					url: '/api/v1/user/logout/',
					type: 'GET',
					data: data,
					contentType: 'application/json; charset=utf-8', 
					success: function(response_text) {
						alert("You are logging out.");
						window.location.assign("/home/");	
					},
					error: function(response_text) {
						alert(response_text);
					}
				});
			});
		},
		index: function(model) {
			new CreateIndex({
				model: model
			}).render().$el.appendTo('#create-editions');
		}
	});
	
	return Router;
});
