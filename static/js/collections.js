define(['jquery', 'underscore', 'backbone', 'models'], function($, _, Backbone, Models) {
	var Collections = {};

	Collections.Modules = Backbone.Collection.extend({ 
		model: Models.Module
	});

	Collections.Slides = Backbone.Collection.extend({
		model: Models.Slide
	});

	Collections.Vocab = Backbone.Collection.extend({
		model: Models.Word
	});

	return Collections;
});
