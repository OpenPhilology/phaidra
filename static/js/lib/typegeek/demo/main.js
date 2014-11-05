requirejs.config({
	'baseUrl': '../',
	'paths': {
		'typegeek': 'src/typegeek'
	},
	'shim': {
		'typegeek': {
			'exports': 'typegeek'
		}
	}
});

require(['typegeek'], function(TypeGeek) {
	new TypeGeek('[data-toggle="typegeek"]');
});
