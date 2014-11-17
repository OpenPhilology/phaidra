define(['jquery', 
	'underscore', 
	'backbone', 
	'models/word', 
	'utils'], 
	function($, _, Backbone, WordModel, Utils) {

		return Backbone.Collection.extend({
			model: WordModel,
			url: '/api/v1/word/',
			comparator: 'CTS',
			initialize: function(models, options) {
				// Keep track of metadata about the collection
				if (!this._meta)
					this._meta = [];

				this.meta = function(prop, value) {
					if (value == undefined)
						return this._meta[prop];
					else
						this._meta[prop] = value;
				};

				if (options && options.url) {
					this.url = options.url;
				}
			},
			parse: function(response) {
				if (response.objects && _.isArray(response.objects.values)) {
					return response.objects.values;		// Lemma detail
				} 
				else if (response.words) {

					// Keep the sentence resource uri when fetching sentences
					response.words.forEach(function(word) {
						word.sentence_resource_uri = response.resource_uri;
					});

					return response.words;				// Sentence detail
				}
				else {
					return response.objects;			// Word/Lemma
				}
			},
			getDefinitions: function(lemma, lemma_resource_uri) {
				// Extract translations
				var alignments = this.extractTranslations(lemma);

				// Pull out most common
				alignments.sort();
				var groups = _.groupBy(alignments);
				alignments = _.compact(alignments.reduce(function(memo, word) {
					var len = groups[word].length;
					(memo[len] || (memo[len] = [])).push(word);
					return memo;
				}, [])).reverse();
				
				return _.uniq(_.flatten(alignments));
			},
			_extractTranslations: function(lemma, target_lang) {
				var instances = this.where({ lemma: lemma });
				var alignments = [];

				// If we find nothing, just return
				if (!instances || instances.length < 1) {
					return alignments;
				}

				// Pull out translations for this word
				instances.forEach(function(instance) {
					alignments.push(this._isolateTranslation(instance, target_lang));
				}.bind(this));

				return alignments;
			},
			_isolateTranslation: function(model, target_lang) {
				if (!model.get('translations') || model.get('translations').length === 0)
					return '';

				// Grab translations in the specified language
				var translations = model.get('translations').filter(function(word) {
					return word.lang === target_lang;
				});
				translations = translations.map(function(word) {
					return this._cleanTranslation(word);
				});

				return translations;
			},
			_cleanTranslation: function(translation, lang) {
				var blacklist = Utils.getVocabBlacklist();
				var alignedWords = translation.reduce(function(memo, word) {
					if (blacklist.indexOf(word.value) === -1)
						memo.push(word.value);
					return memo;
				}, []);
				return alignedWords.join(' ').trim();
			},
			buildPhrase: function(model) {
				console.log(this.models.length);

				var models = this.where({ sentence_resource_uri: model.get('sentence_resource_uri') });

				// Take an array of word models and construct a dataMap
				var words = models.map(function(model) {
					model.attributes.id = model.attributes.tbwid;
					return model.attributes;
				});

				var dataMap = words.reduce(function(map, node) {
					map[node.id] = node;
					return map;
				}, []);

				// Get the parent node of our phrase
				var target_id = model.get('tbwid');
				var node = dataMap[target_id];
				var success = true;

				// Traverse the dataMap till we find the desired ancestor (target)
				while (node.pos !== 'verb') {
					node = dataMap[node.head];
					if (!node || !node.pos) {
						success = false;
						break;
					}
				}

				// Exit if failure
				if (!success) return false;

				// Construct tree
				var target = dataMap[target_id];
				var treeData = [];
				words.forEach(function(node) {
					var head = dataMap[node.head];
					if (head)
						(head.children || (head.children = [])).push(node);
					else
						treeData.push(node);
				});

				// Build the path between the target node and its highest ancestor node
				var path = [];
				while (target !== node) {
					path.push(target);
					target = dataMap[target.head];
				}


				// TODO: Pull this out into separate function
				var results = [node];
				var that = this;
				function _extractChildren(child) {
					var children = child.children;
					if (children) {
						for (var i = 0, child; child = children[i]; i++) {
							if (that._ofInterest(child, path)) {
								results.push(child);
								_extractChildren(child);
							}
						}
					}
				}
				_extractChildren(node);
				
				// Make the results shallow
				results.forEach(function(result) {
					delete result.children;
				});
				results = _.sortBy(results, function(result) { return result.id; });

				// TODO: Something is wrong with _extractChildren function
				// See for example: urn:cts:greekLit:tlg0003.tlg001.perseus-grc:1.91.3
				results = _.uniq(results, false, function(result) { return result.CTS; });

				return results;
			},
			_ofInterest: function(child, path) {
				if (path.indexOf(child) !== -1)
					return true;
				if (child.relation === 'AuxC')
					return false;
				if (child.pos === 'verb')
					return false;
				if (child.pos === 'participle' && (child.relation === 'ADV' || child.relation === 'ADV_CO'))
					return false;

				return true;
			},
			buildAlignmentPhrase: function(phrase, target_lang) {
				// Assumes input from buildPhrase function
				// Alignment editor needs data in a special format, so here we just fill it out.

				// Alignment editor expects an array of lists of words
				// Start with phrase (greek), and build other sentence with alignment data.
				var sentences = [phrase];

				// Pull out the translations we want
				sentences.push(phrase.reduce(function(memo, word) {
					if (word.translations) {
						memo = memo.concat(word.translations.filter(function(w) {
							return w.lang === target_lang;
						}));
					}
					return memo;
				}, []));

				// If alignments for this target language don't exist, return false
				if (sentences[1].length === 0)
					return false;

				// Contruct the second sentence
				var alignments = sentences.map(function(s, i) {
					
					var alignment = {};
					alignment.lang = i === 0 ? s[0].lang : target_lang;

					// Order our sentence
					alignment.words = _.sortBy(s, function(t) {
						return s.lang === 'grc' ? t.id : parseInt(t.CTS.split(':')[5]);
					});
					alignment.words = _.uniq(alignment.words, false, function(t) {
						return t.CTS;
					});
					alignment.words.forEach(function(w) {
						if (w.lang === 'grc')
							return;

						// Find translations that also belong in the phrase
						w.translations = phrase.filter(function(p) {
							if (!p.translations) return false;
							return p.translations.filter(function(t) {
								return w.CTS === t.CTS;
							}).length !== 0;
						});
					});

					// Helper data Morea likes to have (because it normally likes to get data from the API)
					// Normally these would be API endpoints, but we are providing the data so it's not needed
					alignment.translations = {};

					if (i === 0)
						alignment.translations[target_lang] = '/';
					else
						alignment.translations['grc'] = '/';

					alignment.CTS = s[0].CTS.split(':').slice(0, 5).join(':');

					return alignment;

				}.bind(phrase));

				return alignments;
			},
			getTranslatedSentence: function(alignments, target_lang) {
				var sentence = alignments.filter(function(alignment) {
					return alignment.lang === target_lang;
				})[0];

				var translation = sentence.words.reduce(function(memo, word) {
					memo += word.value + ' ';
					return memo;
				}, '').trim() + '.';

				return translation.charAt(0).toUpperCase() + translation.slice(1);
			},
			_createVocabulary: function(options) {
				// Function creates vocab list of lemmas based on frequency in current collection
				if (this.models.length === 0)
					return [];

				var frequencies = _.reduce(this.models, function(map, model) {
					var lemma = model.get('lemma');
					(map[lemma] || (map[lemma] = [])).push(model);
					return map;
				}, {});
				
				var lemmas = _.uniq(Object.keys(frequencies).sort());
				this.meta('vocabulary', lemmas) 

				return this.meta('vocabulary');
			},
			getNextVocab: function() {
				if (!this.meta('vocabulary') && this._createVocabulary().length === 0) {
					return false;
				}

				// Determine the subset of models that match grammar topic
				var subset = this.models.filter(function(model) {
					return this.meta('vocabulary').indexOf(model.get('lemma') !== 0);
				}.bind(this));
				
				// Right now this is random. Should have a better strategy...
				var index = Math.floor((Math.random() * subset.length) + 1) - 1;

				// ZERO -- for testing
				var chosen = subset[index];

				return this.where({ CTS: chosen.get('CTS') })[0];
			}
		});
	}
);
