define(['jquery', 'underscore', 'backbone', 'models', 'collections'], function($, _, Backbone, Models, Collections) { 

	var Router = {};
	Router.Router = Backbone.Router.extend({
		routes: {
			"create/": "index",
		},
		initialize: function() {
			// Create/Populate necessary models and collections

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
		index: function() {
		},

	});
	
	return Router;
});
