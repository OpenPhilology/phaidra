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

require(['jquery', 'underscore', 'backbone', 'd3', 'views/parse_tree', 'bootstrap'], function($, _, Backbone, d3, parseTree) {
	$(document).ready(function() {
		var trees = [];
		var tree = $('.tree');
		for (var i = 0; i < tree.length; i++) {
			trees.push(new parseTree({ container: $(tree[i]) }).render());
		}
	});
});
