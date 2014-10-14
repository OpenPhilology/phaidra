require(['jquery', 'underscore', 'backbone', 'd3', 'bootstrap'], function($, _, Backbone, d3) {
	$(document).ready(function() {
		
		// 2 because of language codes being prepended
		var app = window.location.pathname.split('/')[2];
		
		function activateBootstrap() {
			// Activate Bootstrap JS Components
			$('.module .circle').tooltip({ container: 'body'});
			$('div[data-toggle="tooltip"]').tooltip();
			$('a[data-toggle="tooltip"]').tooltip();
		}

		// TODO: Investigate more flexible ways of doing this 
		switch(app) {
			case "lessons":
			case "module":
				require(['apps/lesson-router'], function(Router) {
					new Router();
					Backbone.history.start({ pushState: true });
					activateBootstrap();
				});
				break;
			case "reader":
				require(['apps/reader-router'], function(Router) {
					new Router();
					Backbone.history.start({ pushState: true });
					activateBootstrap();
				});
				break;
			case "create":
				require(['apps/create-router'], function(Router) {
					new Router();
					Backbone.history.start({ pushState: true });
					activateBootstrap();
				});
				break;
			default:
				require(['apps/default-router'], function(Router) {
					new Router();
					Backbone.history.start({ pushState: true });
					activateBootstrap();
				});
		}
	});
});
