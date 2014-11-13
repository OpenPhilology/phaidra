requirejs.config({
	'baseUrl': '/static/js',
	'paths': {
		// Packages installed by Bower
		'backbone': 'components/backbone/backbone',
		'bootstrap': 'components/bootstrap/dist/js/bootstrap',
		'd3': 'components/d3/d3',
		'jquery': 'components/jquery/dist/jquery',
		'jquery-ui-core': 'components/jquery-ui/ui/core',
		'underscore': 'components/underscore/underscore',
		'jquery-ui-slide': 'components/jquery-ui/ui/effect-slide',
		'json2': 'components/json2/json2',
		'text': 'components/requirejs-text/text',

		// Included as git submodules
		'daphne': 'lib/daphnejs/src/daphne',
		'morea': 'lib/moreajs/src/morea',
		'typegeek': 'lib/typegeek/src/typegeek'
	},
	'shim': {
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
		'daphne': {
			'exports': 'daphne',
			'deps': ['d3']
		},
		'jquery-ui-core': {
			'deps': ['jquery']
		},
		'jquery-ui-slide': {
			'deps': ['jquery', 'jquery-ui-core']
		},
		'morea': {
			'exports': 'morea'
		},
		'underscore': {
			'exports': '_'
		}
	}
});
