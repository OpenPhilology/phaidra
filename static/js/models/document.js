define(['jquery', 'underscore', 'backbone', 'utils', 'collections/words'], function($, _, Backbone, Utils) {

	return Backbone.Model.extend({

		defaults: {
			'modelName': 'document'
		},
		initialize: function(attributes) {
			this.urlRoot = attributes.resource_uri;

			WordsCollection = require('collections/words');
			this.words = new WordsCollection();
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
		},
		getNextCTS: function(CTS) {
			var current_resource_uri = '';

			// If they're giving us a document or work-level CTS, derive the sentence-level
			if (CTS.split(':')[4].split('.').length !== 3) {
				current_resource_uri = this.words.at(1).get('sentence_resource_uri');
			}
			else {
				var current_resource_uri = this.words.findWhere({
					sentenceCTS: CTS
				}).get('sentence_resource_uri');
			}

			var index = this.get('sentences').indexOf(current_resource_uri) + 1;
			var nextPage = this.words.findWhere({
				sentence_resource_uri: this.get('sentences')[index]
			})

			if (nextPage)
				return nextPage.get('sentenceCTS');
			else
				return undefined;
		},
		getPrevCTS: function(sentenceCTS) {
			var current_resource_uri = this.words.findWhere({
				sentenceCTS: sentenceCTS
			}).get('sentence_resource_uri');
			var index = this.get('sentences').indexOf(current_resource_uri) - 1;
			var nextPage = this.words.findWhere({
				sentence_resource_uri: this.get('sentences')[index]
			})

			if (nextPage)
				return nextPage.get('sentenceCTS');
			else
				return undefined;
		},
		populate: function(sentenceCTS, options) {
			// Populate a section of words by their sentence CTS id
			var target = this.words.findWhere({ sentenceCTS: sentenceCTS });

			var that = this;
			this.words.url = target.get('sentence_resource_uri');
			this.words.fetch({
				merge: true,
				remove: false,
				success: that.populateWordsSuccess.bind(that),
				error: that.populateWordsError.bind(that)
			});
		},
		populateWordsSuccess: function(collection, response, options) {
			collection.meta('translations', response.translations);
			this.trigger('populated', this, response.CTS);
		},
		populateWordsError: function(collection, response, options) {
			Utils.displayNotification('Document Error', 'Could not load document.', {
				btnName: 'Back to Index',
				state: 'error',
				url: '/'
			});
		}
	});

});
