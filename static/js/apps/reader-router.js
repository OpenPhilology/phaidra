define(['jquery', 'underscore', 'backbone', 'models', 'collections', 'views/reader'], function($, _, Backbone, Models, Collections, ReaderView) { 

	var Router = {};
	Router.Router = Backbone.Router.extend({
		routes: {
			"reader/:cts": "updateReader",
			"reader/": "showReader",
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

		// Reader Routes
		showReader: function() {
			this.updateReader(undefined);
		},
		updateReader: function(CTS) {
			if (!this.reader_view) {
				this.reader_view = new ReaderView({ 
					el: '#reader', 
					CTS: CTS 
				}).render();
			}
			else {
				this.reader_view.turnToPage(CTS);
			}
		}
	});
	
	return Router;
});
