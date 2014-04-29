requirejs.config({
	'baseUrl': '/static/js',
	'paths': {
		// Lib paths
		'jquery': 'lib/jquery-2.0.3',
		'bootstrap': '../bootstrap/js/bootstrap.min',
		'json2': 'lib/json2',
		'underscore': 'lib/underscore-min',
		'backbone': 'lib/backbone',
		'd3': 'lib/d3.v3.min',
		'jquery-ui': 'lib/jquery-ui-draggable',
		'text': 'lib/text'
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
		},
		'd3': {
			'exports': 'd3'
		}
	}
});

require(['jquery', 'underscore', 'backbone', 'router', 'd3', 'bootstrap'], function($, _, Backbone, Phaidra, d3) {
	$(document).ready(function() {
		var app = new Phaidra.Router();
		Backbone.history.start({ pushState: true });

		// Activate Bootstrap JS Components
		//$('.sec').tooltip();
		$('.module .circle').tooltip({ container: 'body'});
		$('div').tooltip();
		$('a').tooltip();
	});
});
