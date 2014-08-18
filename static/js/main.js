require(['jquery', 'underscore', 'backbone', 'd3', 'bootstrap'], function($, _, Backbone, d3) {
	$(document).ready(function() {
		
		var app = window.location.pathname.split('/')[1];
		
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
				require(['apps/lesson-router'], function(Lessons) {
					new Lessons.Router();
					Backbone.history.start({ pushState: true });
					activateBootstrap();
				});
				break;
			case "reader":
				require(['apps/reader-router'], function(Reader) {
					new Reader.Router();
					Backbone.history.start({ pushState: true });
					activateBootstrap();
				});
				break;
			case "create":
				require(['apps/create-router'], function(Create) {
					new Create.Router();
					Backbone.history.start({ pushState: true });
					activateBootstrap();
				});
				break;
			default:
				require(['apps/default-router'], function(Default) {
					new Default.Router();
					Backbone.history.start({ pushState: true });
					activateBootstrap();
				});
		}


	});
});
