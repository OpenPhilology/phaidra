define(['jquery', 'underscore', 'backbone', 'models/word', 'utils'], function($, _, Backbone, WordModel, Utils) {

	return Backbone.Collection.extend({
		model: WordModel,
		url: '/api/v1/word/',
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
			
			if (options) {
				this.meta('grammar', options.grammar);

				if (options.topic) {
					this.meta('topic', options.topic);
					this.url = '/api/v1/word/?' + options.topic.get('query');
				}
			}
		},
		parse: function(response) {
			return response.objects;
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
			var index = Math.floor((Math.random() * this.models.length) + 1);
			return this.at(index);
		}
	});

});
