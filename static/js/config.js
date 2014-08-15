requirejs.config({
	'baseUrl': '/static/js',
	'paths': {
		// Lib paths
		'jquery': 'lib/jquery-2.1.1',
		'bootstrap': '../bootstrap/js/bootstrap.min',
		'json2': 'lib/json2',
		'underscore': 'lib/underscore-min',
		'backbone': 'lib/backbone',
		'd3': 'lib/d3.v3.min',
		'jquery-ui': 'lib/jquery-ui-draggable',
		'jquery-ui-core': 'lib/jquery-ui-core',
		'jquery-ui-slide': 'lib/jquery-ui-effects-slide',
		'text': 'lib/text',
		'daphne': 'lib/daphnejs/src/daphne',
		'morea': 'lib/moreajs/src/morea'
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
		},
		'morea': {
			'exports': 'morea'
		},
		'daphne': {
			'exports': 'daphne',
			'deps': ['d3']
		},
		'jquery-ui-core': {
			'deps': ['jquery']
		},
		'jquery-ui': {
			'deps': ['jquery']
		},
		'jquery-ui-slide': {
			'deps': ['jquery', 'jquery-ui-core']
		}
	}
});
