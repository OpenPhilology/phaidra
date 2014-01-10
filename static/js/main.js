requirejs.config({
	'baseUrl': '/static/js',
	'paths': {
		// Lib paths
		'jquery': 'lib/jquery-2.0.3',
		'bootstrap': '../bootstrap/js/bootstrap',
		'json2': 'lib/json2',
		'underscore': 'lib/underscore-min',
		'backbone': 'lib/backbone',
		'd3': 'lib/d3.v3.min'
	},
	'shim': {
		'underscore': {
			'exports': '_'
		},
		'backbone': {
			'deps': ['jquery', 'underscore'],
			'exports': 'Backbone'
		},
		'bootstrap': {
			'deps': ['jquery']
		}
	}
});

require(['jquery', 'underscore', 'backbone', 'router'], function($, _, Backbone, Phaidra) {
	$(document).ready(function() {
		var app = new Phaidra.Router();
		Backbone.history.start({ pushState: true });

		// Activate Bootstrap JS Components
		//$('.sec').tooltip();
		//$('.module .circle').tooltip({ container: 'body'});
	});
});
