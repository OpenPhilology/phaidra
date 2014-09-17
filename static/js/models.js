define(['jquery', 'underscore', 'backbone', 'utils'], function($, _, Backbone, Utils) {
	var Models = {};

	Models.User = Backbone.Model.extend({
		defaults: {
			'modelName': 'user',
		},
		url: '/api/v1/user/',
		parse: function(response) {
			if (response && response.meta)
				this.meta = response.meta;
			this.set(response.objects.filter(function(obj) {
				return obj.username === U;
			})[0]);
			this.set("locale", locale);
			this.set("language", locale.split('-')[0]);
		}
	});

	Models.Lesson = Backbone.Model.extend({
		defaults: {
			'modelName': 'lesson'
		}
	});

	Models.Slide = Backbone.Model.extend({
		initialize: function() {
			_.bindAll(this, 'checkAnswer');
		},
		constructor: function(attributes, options) {
			Backbone.Model.prototype.constructor.call(this, attributes);

			this.collection = options.collection;
			this.options = options;
			this.attributes = attributes;
		},
		defaults: {
			'modelName': 'slide',
		},
		populate: function(options) {
			// Allows us to lazy-load everything
			if (this.get('includeHTML'))
				this.fetchHTML(options);
			else if (this.get('task'))
				this.fillAttributes(options);
		},
		fetchHTML: function(options) {
			var that = this;
			if (this.get('content')) {
				this.set('populated', true);
				if (options && options.success) options.success();

				return;
			}

			// Fetch HTML if needed
			$.ajax({
				url: that.get('includeHTML'),
				dataType: 'text',
				success: function(response) {
					that.set('content', response);
					that.set('populated', true);
					if (options && options.success) options.success();
				},
				error: function(x, y, z) {
					console.log(x, y, z);
				}
			});
		},
		fillAttributes: function(options) {
			var that = this;
			var s = this.get('smyth');
			var entry = Utils.Smyth[s];
			
			var vocab = this.collection.meta('vocab');
			var candidates = vocab.filterVocabulary();
			console.log(candidates);

			if (entry) {
				var url = '/api/v1/' + this.get('endpoint') + '/?format=json&' + entry.query;

				$.ajax({
					url: url,
					dataType: 'text',
					success: function(response) {
						
						var objs = JSON.parse(response).objects;
						var groups = _.groupBy(objs, function(o) {
						   return o.lemma;
						});
						var keepers = objs.filter(function(o) {
							return groups[o.lemma].length > 1;
						});

						var toUse = keepers.length === 0 ? objs : keepers;
						var chosen = _.shuffle(toUse).splice(0, 1)[0];
						
						var answer = chosen[that.get('answerField')];
						that.set('answers', [answer]);
						that.set('encounteredWords', [chosen.CTS]);

						// Treat question like template string to splice in value
						var data = {};
						data[that.get('endpoint')] = chosen.value;
						var compiled = _.template(that.get('question'));
						that.set('question', compiled(data));
						that.set('populated', true);
						if (options && options.success) options.success();
					},
					error: function(x, y, z) {
						console.log(x, y, z);
					}
				});
			}
		},
		checkAnswer: function(attempt) {

			if (this.get('type') === 'slide_direct_select') {
				var correct = true;

				if (typeof(attempt) == 'string')
					attempt = [attempt]

				// Check if all submitted attempts are somewhere in answers
				if (this.get('require_all').toString() === "false") {
					for (var i = 0; i < attempt.length; i++)
						if (this.get('answers').indexOf(attempt[i]) == -1)
							correct = false;

					correct = correct ? true: false;
				}
				// Require order implies that require_all is also true
				else if (this.get('require_order').toString() === "true") {
					if (this.get('answers').length !== attempt.length)
						correct = false;
					else {
						for (var i = 0; i < attempt.length; i++) {
							if (attempt[i] != this.get('answers')[i]) 
								correct = false;
						}

						correct = correct ? true : false;
					}
				}
				// All Required, but order is not required
				else if (this.get('require_all').toString() === "true" && this.get('require_order').toString() === "false")
					correct = $(attempt).not(this.get('answers')).length == 0 && $(this.get('answers')).not(attempt).length == 0;
				else
					correct = false;

				this.set('accuracy', (correct ? 100 : 0));
			}
			else if (this.get('type') === 'slide_info') {
				// Means we are manually checking in either morea.js or daphne.js
				if (!attempt)
					attempt = this.get('response');
			}

			this.set('endtime', (new Date()));
			this.sendSubmission(attempt);

			return correct;
		},
		sendSubmission: function(attempt) {
			var data = {
				response: JSON.stringify(attempt),
				task: this.get('task') || 'static_exercise',
				accuracy: this.get('accuracy'),
				encounteredWords: this.get('encounteredWords'),
				slideType: this.get('type'),
				smyth: this.get('smyth') || undefined,
				timestamp: this.get('endtime').toISOString(),
				starttime: this.get('starttime').toISOString()
			};

			$.ajax({
				url: '/api/v1/submission/',
				headers: { 'X-CSRFToken': window.csrf_token },
				data: JSON.stringify(data),
				processData: false,
				dataType: 'json',
				contentType: "application/json",
				type: 'POST',
				success: function(response) {
					console.log("Successfully submitted data");
				},
				error: function(x, y, z) {
					console.log(x, y, z);
				}
			});
		}
	});

	Models.Document = Backbone.Model.extend({
		defaults: {
			'modelName': 'document'
		},
		initialize: function(attributes) {
			this.urlRoot = attributes.resource_uri;

			Collections = require('collections');
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
			var starter = this.words.findWhere({ sentenceCTS: sentenceCTS });
			var that = this;

			if (starter.get('lemma')) {
				// If it has a lemma property, we know its been populated
				this.trigger('populated', this, { CTS: sentenceCTS });
			}
			else {
				$.ajax({
					url: starter.get('sentence_resource_uri'),
					dataType: 'json',
					doc: that,
					options: options,
					success: function(response) {
						this.doc.set('translations', response.translations);
						
						for (var i = 0; i < response.words.length; i++) {
							var target = this.doc.words.findWhere(
								{ wordCTS: response.words[i]["CTS"] }
							);
							target.set(response.words[i])
						}

						this.doc.trigger('populated', this.doc, { CTS: response["CTS"] });
					},
					error: function(x, y, z) {
						console.log(x, y, z);
					}
				});
			}
		}
	});

	Models.UserDocument = Backbone.Model.extend({
		defaults: {
			modelName: 'user_document'
		},
		initialize: function(attributes) {
			this.urlRoot = attributes.resource_uri;

			Collections = require('collections');
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

	Models.Word = Backbone.Model.extend({
		defaults: {
			'modelName': 'word',
			'selected': false
		},
		initialize: function(attributes) {
			this.set('wordCTS', attributes.sentenceCTS + ':' + (attributes.index + 1));
		},
		urlRoot: function() {
			return this.get('resource_uri');
		},
		parse: function(response) {
			this.set(response);
			this.set('translated', true);
		},
		// TODO: Flesh out this implementation to cover more query filters
		getGrammar: function() {
			var that = this;

			if (this.get('grammar'))
				return this.get('grammar');

			// Go through Smyth and get the relevant topics
			var matches = _.filter(Utils.Smyth, function(entry, key) {

				// If the query isn't relevant to figuring out grammar topics
				if (!entry.query)
					return false;

				var attrs = entry.query.split('&');
				for (var i = 0; i < attrs.length; i++) {

					// Try to make this legible...
					var v = attrs[i].split('=');
					var prop = v[0], value = v[1]; 
					
					if (prop.indexOf('__contains') != -1) {
						prop = prop.substring(0, prop.indexOf('__contains'));
						if (that.get(prop).indexOf(value) == -1)
							return false;
					}
					else if (prop.indexOf('__endswith') != -1) {
						var j = prop.indexOf('__endswith');
						prop = prop.substring(0, j);
						if (that.get(prop).indexOf(value) != (that.get(prop).length - value.length))
							return false;	
					}
					else {
						// Last, simple value check
						if (that.get(prop) != value)
							return false;
					}

				}
				entry.key = key;
				return true;
			}).reverse();

			this.set('grammar', matches);
			
			return this.get('grammar');
		}
	});

	return Models;
});
