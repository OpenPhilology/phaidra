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
		'jquery-ui-core': 'lib/jquery-ui-core',
		'jquery-ui-slide': 'lib/jquery-ui-effects-slide',
		'text': 'lib/text',
		'daphne': 'lib/daphnejs/src/daphne'
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

require(['jquery', 'underscore', 'backbone', 'router', 'd3', 'bootstrap'], function($, _, Backbone, Phaidra, d3) {
	$(document).ready(function() {
		var app = new Phaidra.Router();
		Backbone.history.start({ pushState: true });

		// Activate Bootstrap JS Components
		$('.module .circle').tooltip({ container: 'body'});
		$('div[data-toggle="tooltip"]').tooltip();
		$('a[data-toggle="tooltip"]').tooltip();

		/* Make our SVGs manipulatable via JS
		jQuery('img.svg').each(function(){
			var $img = jQuery(this);
			var imgID = $img.attr('id');
			var imgClass = $img.attr('class');
			var imgURL = $img.attr('src');

			jQuery.get(imgURL, function(data) {
			// Get the SVG tag, ignore the rest
			var $svg = jQuery(data).find('svg');

			// Add replaced image's ID to the new SVG
			if(typeof imgID !== 'undefined') {
				$svg = $svg.attr('id', imgID);
			}
			// Add replaced image's classes to the new SVG
			if(typeof imgClass !== 'undefined') {
				$svg = $svg.attr('class', imgClass+' replaced-svg');
			}

			// Remove any invalid XML tags as per http://validator.w3.org
			$svg = $svg.removeAttr('xmlns:a');

			// Replace image with new SVG
			$img.replaceWith($svg);

			}, 'xml');
		});*/
	});
});
