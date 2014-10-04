define(['jquery', 'underscore', 'backbone', 'utils'], function($, _, Backbone, Utils) {
	return Backbone.Model.extend({
		defaults: {
			modelName: 'user_document'
		},
		initialize: function(attributes) {
			this.urlRoot = attributes.resource_uri;

			Collections = require('collections/words');
			this.words = new Collections.Words();
		},
		parse: function(response) {

			// Set direction of language
			var textDir = response.lang === 'fas' ? 'rtl' : 'ltr';
			this.set('direction', textDir);

			// Give our document a human-readable language name
			this.set('readable_lang', Utils.getReadableLang(this.get('lang')));
			this.set('translations', response.translations);

			// Split all the words and add them to the collection.
			for (var i = 0; i < response.sentences.length; i++) {
				var tokens = response.sentences[i]["sentence"].trim().split(' ');

				this.words.add(tokens.map(function(token, index) {
					return {
						sentenceCTS: response.sentences[i]["CTS"],
						sentence_resource_uri: response.sentences[i]["resource_uri"],
						lang: response.lang,
						value: token,
						index: index
					};
				}));
			}
		}
	});

});
