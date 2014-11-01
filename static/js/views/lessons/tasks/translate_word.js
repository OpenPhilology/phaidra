define(['jquery', 'underscore', 'backbone', 'models/word', 'collections/words', 'utils', 'text!/templates/js/lessons/tasks/translate_word.html'], function($, _, Backbone, WordModel, WordsCollection, Utils, Template) {

	var View = Backbone.View.extend({
		template: _.template(Template),
		tagName: 'div',
		className: 'subtask',
		initialize: function(options) {
			this.options = options;
		},
		render: function() {
			this.phrase = this.model.getPhrase();
			this.defs = this.model.getDefinition();

			// !!!!! IMPORTANT !!!!!
			// Here we determine if a phrase can be made from our starter word.
			// If we cannot, then we must select a new model within the collection and destroy this view

			if (!this.phrase || !this.defs) {
				this.remove();
				return false;
			}

			var alignment = this.constructPhrase(this.phrase);

			this.$el.html(this.template({
				model: this.model,
				sentence: this.makeSampleSentence(alignment[0], 'open'),
			}));

			return this;
		},
		constructPhrase: function(phrase) {
			// Construct phrasal alignment data
			var sentences = [phrase];
			sentences.push(phrase.reduce(function(memo, word) {
				if (word.translations) {	
					memo = memo.concat(word.translations.filter(function(w) { 
						return w.lang === LOCALE; 
					}));
				}
				return memo;
			}, []));

			if (sentences[1].length === 0) {
				alert('We don\'t have alignment data for: ' + LOCALE);
			}

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
		makeSampleSentence: function(sentence, state) {
			// State: open, correct, incorrect
			state = state || 'open';

			return _.map(sentence.words, function(s) {
				if (state === 'open')
					return s.value === this.model.get('value') ? new Array(s.value.length + 1).join('_') : s.value;
				else if (state === 'correct')
					return s.value === this.model.get('value') ? ('<span class="correct">' + s.value + '</span>') : s.value;
				else if (state === 'incorrect')
					return s.value === this.model.get('value') ? ('<span class="incorrect">' + s.value + '</span>') : s.value;
			}.bind(this)).join(' &nbsp; ');
		}
	});

	return View;
});
