define(['jquery', 'underscore', 'backbone', 'models/word', 'utils'], function($, _, Backbone, WordModel, Utils) {

	return Backbone.Collection.extend({
		model: WordModel,
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

			if (options && options.grammar) 
				this.meta('grammar', options.grammar);
		},
		add: function(newWord) {
			newWord = _.isArray(newWord) ? newWord : [newWord];	
			var duplicates = [];
			for (var i = 0, word; word = newWord[i]; i++) {
				var dup = this.any(function(w) {
					return w.equiv(word);
				}.bind(this));
				if (dup) duplicates.push(word);
			};
			duplicates = _.compact(duplicates);
			
			// Carefully merge in duplicates
			duplicates.forEach(function(d) {
				var model = this.findWhere({ CTS: d.CTS });
				var keys = Object.keys(model.attributes);
				for (var key in model.attributes) {
					if (d[key]) model.set(key, d[key]);
				}
			}.bind(this));

			Backbone.Collection.prototype.add.call(this, newWord);
		},
		populateVocab: function(collection) {

			var that = this;
			var calls = [];

			// First, see if there are queries associated with these smyth units
			var queries = _.uniq(_.compact(_.pluck(Utils.Smyth.filter(function(s) {
				return s.ref.split('#')[0] === that.meta('grammar');
			}), 'query')));
			queries = queries.length === 0 ? [""] : queries;
			
			// If there's no explicit query, then returning any word is fine
			queries.forEach(function(query, i, arr) {
				calls.push($.ajax({
					url: '/api/v1/word?' + query,
					data: { "limit": 300 },
					success: function(response) {
						that.add(response.objects);			
					},
					error: function(x, y, z) {
						console.log(x, y, z);
					}
				}));
			});

			$.when.apply(this, calls).done(triggerPopulated);

			function triggerPopulated() {
				that.meta('populated', true);
				that.trigger('populated');
			}
		},
		filterVocabulary: function() {
			if (this.models.length === 0) return [];

			var groupedByFreq = _.reduce(this.models, function(map, model) {
				var lemma = model.attributes.lemma;
				(map[lemma] || (map[lemma] = [])).push(model);
				return map;
			}, {});
			
			var candidates = [];

			// Try to get good definitions based on what alignment data is likely to be like
			switch(this.models[0].get('pos')) {
				case 'noun':
					candidates = this.where({ 'case': 'gen', 'number': 'sg' });
					break;
				case 'verb':
					candidates = this.where({ 'pos': 'verb' });
					break;
				case 'adj':
					candidates = this.where({ 'gender': 'fem' });
					break;
				default:
					candidates = this.where({ 'lang': 'grc' });
					break;
			}

			candidates = _.uniq(_.map(candidates, function(c) { return c.get('lemma'); }));
			return candidates;
		},
		getNextRandom: function(ref, model) {
			var candidates = this.models.filter(function(m) {
				var found = _.pluck(m.getGrammar(), 'ref').indexOf(ref) !== -1;
				if (model !== undefined) {
					found = found && model.get('lemma') !== m.get('lemma');
				}
				return found;
			}.bind(this));

			var index = Math.floor((Math.random() * candidates.length) + 1);
			var next = this.findWhere({ lemma: candidates[index].get('lemma') });

			return next;
		}
	});

});
