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
		// TODO: Refactor this
		populate: function(options) {
			if (this.get('populated')) {
				if (options && options.success) options.success();
				return;
			}

			// Allows us to lazy-load everything
			if (this.get('includeHTML'))
				this.fetchHTML(options);
			else if (this.get('task'))
				this.fillAttributes(options);
			else if (this.get('type') !== 'slide_vocab') {
				this.set('populated', true);
				if (options && options.success) options.success();
			}
			else if (this.get('type') === 'slide_vocab') {
				if (this.collection.meta('vocab').meta('populated')) {
					if (options && options.success) options.success();
				}
				else {
					this.collection.meta('vocab').on('populated', options.success, this);
				}
			}
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
					if (options && options.error) options.error();
					console.log(x, y, z);
				}
			});
		},
		fillAttributes: function(options) {
			var that = this;
			var s = this.get('smyth');
			var entry = Utils.Smyth[s];

			// This differs based on if they loaded an exercise slide first, or started at beginning
			function useVocab() {
				if (!entry)
					return;
					
				var vocab = that.collection.meta('vocab');
				var candidates = vocab.filterVocabulary();
				that.collection.meta('vocab').meta('candidates', candidates);

				// Pick an example based on vocab for this unit
				var chosen = _.shuffle(_.filter(vocab.models, function(v) {
					return candidates.indexOf(v.get('lemma')) !== -1;
				})).splice(0, 1)[0];

				that.set('answers', [chosen.get(that.get('answerField'))]);
				that.set('encounteredWords', [chosen.get('CTS')]);

				// Treat question like template string to splice in value
				var data = {};
				data[that.get('endpoint')] = chosen.get('value');
				var compiled = _.template(that.get('question'));

				that.set('question', compiled(data));
				that.set('populated', true);
				if (options && options.success) options.success();
			}
			useVocab.bind(this);

			if (this.collection.meta('vocab').meta('populated'))
				useVocab();
			else
				this.collection.meta('vocab').on('populated', useVocab, this);

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
		equiv: function(other) {
			return this.get('CTS') === other.CTS;
		},
		getDefinition: function(lang) {
			if (!this.get('translations') || !this.get('translations').length) return false;
			if (this.get('alignments')) return this.get('alignments');

			lang = lang || 'en';

			function extractTranslations(wordModel) {
				if (!wordModel.get('translations') || wordModel.get('translations').length === 0) return []; 

				var translations = wordModel.get('translations').filter(function(t) {
					return t.lang === lang;
				});
				var blacklist = Utils.getVocabBlacklist(wordModel.get('pos'));

				var alignedWords = translations.reduce(function(memo, word) {
					if (blacklist.indexOf(word.value) === -1)
						memo.push(word.value);
					return memo;
				}, []);
				
				return alignedWords.join(' ').trim();
			}

			var alignments = [extractTranslations(this)];

			// If other instances of this lemma exist, with translations, include those.
			var instances = this.collection.where({ lemma: this.get('lemma') });
			if (instances && instances.length > 1) {
				instances.forEach(function(inst) {
					var words = extractTranslations(inst);
					if (words.length > 0 && inst.get('pos') !== 'participle') {
						alignments.push(words);
					}
				});
			}

			// Pull out the most common ones
			alignments.sort();
			var groups = _.groupBy(alignments);
			alignments = _.compact(alignments.reduce(function(memo, a) {
				var len = groups[a].length;
				(memo[len] || (memo[len] = [])).push(a + '  (' + len + ')');
				return memo;
			}, [])).reverse();
			alignments = _.uniq(_.flatten(alignments));

			this.set('alignments', alignments);

			return alignments;
		},
		getVocabChoices: function() {
			var answer = Utils.stripVocabCount(this.getDefinition()[0]);
			var others = []; 
			var shuffled = _.shuffle(this.collection.models);
			for (var i = 0, model; model = shuffled[i]; i++) {
				if (others.length < 6) {
					word = model.getDefinition();
					if (!word) continue;

					word = Utils.stripVocabCount(word[0]);
					if (word.indexOf(answer) === -1) others.push(word);
				}
			}
			others.push(answer);
			return others;
		},
		fetchAlternativeDefinitions: function(options) {
			var query = this.get('lemma_resource_uri');
			var that = this;

			$.ajax(query, {
				data: { full: true, limit: 20 },
				success: function(response) {
					for (var i = 0, value; value = response.values[i]; i++) {
						var target = that.collection.findWhere({ CTS: value.CTS });
						if (!target)
							that.collection.add(value);
						else {
							target.set(value);
						}
					}
					if (options && options.success) options.success();	
					that.set('populated', true);
				},
				error: function(x, y, z) {
					if (options && options.error) options.error();
				}
			});
		},
		getDictForm: function() {
			var form = '';

			switch (this.get('pos')) {
				case 'verb':
					form = this.get('lemma');
					break;
				case 'noun':
					form = Utils.getDefiniteArticle(this.get('gender'), 'sg') + ' '; 
					form += this.get('lemma');

					// Try to find the genitive
					var gen = this.collection.findWhere({ 'lemma': this.get('lemma'), 'case': 'gen', 'number': 'sg' });
					if (gen) form += ', ' + gen.get('value');

					break;
				case 'adj':
					form = this.get('lemma');
					break;
				default:
					form = this.get('lemma');
					break;
			}

			return form;
		},
		getPhrase: function() {
			
			var words = this.collection.where({ sentence_resource_uri: this.get('sentence_resource_uri') });
			words = words.map(function(word) {
				word.attributes.id = word.attributes.tbwid;
				return word.attributes;
			});

			var dataMap = words.reduce(function(map, node) {
				map[node.id] = node;
				return map;
			}, []);

			var instance = this.get('tbwid');
			var node = dataMap[instance];
			var success = true;
			while (node.pos !== 'verb') {
				node = dataMap[node.head];
				if (!node || !node.pos) {
					success = false;
					break;
				}
			}

			if (!success) return false;

			var treeData = [];
			var target = dataMap[instance]; 
			words.forEach(function(node) {
				var head = dataMap[node.head];
				if (head)
					(head.children || (head.children = [])).push(node);
				else
					treeData.push(node);
			});

			var path = [];
			while (target !== node) {
				path.push(target);
				target = dataMap[target.head];
			}

			var results = [node];
			function extractChildren(child) {
				var children = child.children;
				if (children) {
					for (var i = 0, child; child = children[i]; i++) {
						if (ofInterest(child)) {
							results.push(child);
							extractChildren(child);
						}
					}
				}
			}
			function ofInterest(child) {
				if (path.indexOf(child) !== -1) return true;
				if (child.relation === 'AuxC') return false;
				if (child.pos === 'verb') return false;
				if (child.pos === 'participle' && (child.relation === 'ADV' || child.relation === 'ADV_CO')) return false;

				return true;
			}
			extractChildren(node);

			results.forEach(function(r) {
				delete r.children;
			});
			results =  _.sortBy(results, function(r) { return r.id; });
			
			// TODO Something is wrong with our extractChildren function.
			// See for example: urn:cts:greekLit:tlg0003.tlg001.perseus-grc:1.91.3
			results = _.uniq(results, false, function(r) { return r.CTS; });

			return results;
		},
		fetchSentence: function(wordCTS, options) {
			// Populate a section of words by their sentence CTS id
			var starter = this.collection.findWhere({ CTS: wordCTS });
			var that = this;
			var sentence = this.collection.filter(function(model) {
				return starter.get('sentence_resource_uri') === model.get('sentence_resource_uri');
			});
				
			// If it has a lemma property, we know its been populated
			if (starter.get('populated')) {
				this.trigger('change:populated');
			}
			else {
				$.ajax({
					url: starter.get('sentence_resource_uri'),
					dataType: 'json',
					model: that,
					data: { full: true },
					options: options,
					success: function(response) {
						for (var i = 0; i < response.words.length; i++) {
							response.words[i].sentence_resource_uri = starter.get('sentence_resource_uri');
							this.model.collection.add(response.words[i]);
						}

						// Now go fetch alternative definitions for this word based on lemma
						this.model.fetchAlternativeDefinitions();
					},
					error: function(x, y, z) {
						console.log(x, y, z);
					}
				});
			}
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
