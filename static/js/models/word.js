define(['jquery', 'underscore', 'backbone', 'utils'], function($, _, Backbone, Utils) {

	return Backbone.Model.extend({
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
		getDefinition: function(lang, thisModelOnly) {
			if (!this.get('translations') || !this.get('translations').length) return false;
			if (this.get('alignments') && !thisModelOnly) return this.get('alignments');

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

			// If you only want the translation for this exact model, not all models with this lemma 
			if (thisModelOnly) 
				return extractTranslations(this);

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
				(memo[len] || (memo[len] = [])).push(a);
				return memo;
			}, [])).reverse();
			alignments = _.uniq(_.flatten(alignments));

			this.set('alignments', alignments);

			return alignments;
		},
		constructPhrase: function(phrase) {
			// Construct phrasal alignment data
			var sentences = [phrase];
			sentences.push(phrase.reduce(function(memo, word) {
				if (word.translations) {	
					memo = memo.concat(word.translations.filter(function(w) { 
						return w.lang === 'en'; 
					}));
				}
				return memo;
			}, []));

			var alignments = sentences.map(function(s, i) {
				var alignment = {};
				alignment.lang = s[0].lang;
				alignment.words = _.sortBy(s, function(t) { 
					return s.lang === 'grc' ? t.id : parseInt(t.CTS.split(':')[5]); 
				});
				alignment.words = _.uniq(alignment.words, false, function(t) {
					return t.CTS;
				});
				alignment.words.forEach(function(w) {
					if (w.lang === 'grc') return;
					
					w.translations = phrase.filter(function(p) {
						if (!p.translations) return false;
						return p.translations.filter(function(t) {
							return w.CTS === t.CTS;
						}).length !== 0;
					});
				});

				alignment.translations = i === 0 ? { 'en': '/' } : { 'grc': '/' }; 
				alignment.CTS = s[0].CTS.split(':').slice(0, 5).join(':');
				return alignment;
			}.bind(phrase));

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
						this.model.fetchAlternativeDefinitions(options);
					},
					error: function(x, y, z) {
						console.log(x, y, z);
					}
				});
			}
		},
		getHumanReadableMorph: function() {
			var attrs = [];
			switch (this.get('pos')) {
				case 'verb':
					attrs.push(Utils.getHumanReadableMorph(this.get('person')), 
						Utils.getHumanReadableMorph(this.get('number')), 
						Utils.getHumanReadableMorph(this.get('tense')),
						Utils.getHumanReadableMorph(this.get('voice')),
						Utils.getHumanReadableMorph(this.get('mood')));
					break;
				default:
					attrs.push(Utils.getHumanReadableMorph(this.get('case')), 
						Utils.getHumanReadableMorph(this.get('number')), 
						Utils.getHumanReadableMorph(this.get('gender')));
					break;
			}

			return attrs.join(', ');
		},
		// TODO: Flesh out this implementation to cover more query filters
		getGrammar: function() {
			var that = this;

			if (this.get('grammar'))
				return this.get('grammar');

			// Go through Smyth and get the relevant topics
			var matches = _.filter(Utils.Smyth, function(entry) {

				// If the query isn't relevant to figuring out grammar topics
				if (!entry.query || (entry.require === false))
					return false;

				var attrs = entry.query.split('&');

				for (var i = 0, attr; attr = attrs[i]; i++) {

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
					// Last, simple value check
					else if (that.get(prop) != value) {
						return false;
					}

				}
				return true;
			}).reverse();

			this.set('grammar', matches);
			
			return this.get('grammar');
		}
	});

});
