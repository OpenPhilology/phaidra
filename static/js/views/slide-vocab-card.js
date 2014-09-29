define(['jquery', 'underscore', 'backbone', 'models', 'collections', 'text!/templates/js/slide-vocab-card.html', 'morea', 'daphne', 'utils'], function($, _, Backbone, Models, Collections, Template, Morea, Daphne, Utils) {
	var View = Backbone.View.extend({
		events: { 
			'submit form': 'checkAnswer'
		},
		template: _.template(Template),
		initialize: function(options) {
			this.model.on('change:populated', this.render, this);
			this.model.fetchSentence(this.model.get('CTS'));
		},
		render: function(options) {
			var phrase = this.model.getPhrase();
			var defs = this.model.getDefinition();

			// TODO: Deal with defaults
			if (!options) {
				var options = {}; 
				options.answer = 'open';
			}
			
			// If our data's fucked, don't bother
			if (!phrase || !defs) {
				this.model.set('active', false);		// Deactivate this slide

				// Activate a new one -- TODO: find an intelligent way to do this?!
				var lemmas = $('.card[data-lemma]').map(function(i, n) { return n.dataset.lemma });
				var i = Math.floor((Math.random() * lemmas.length) + 1);
				this.collection.findWhere({ lemma: lemmas[i] }).set('active', true);

				console.log("removing view for " + this.model.get('lemma'));

				// Destroy this view
				this.remove();
				return;
			}
			else {
				console.log("creating view for " + this.model.get('lemma'));
			}

			var alignment = this.constructPhrase(phrase);

			this.$el.html(this.template({
				model: this.model,
				defs: defs,
				sentence: this.makeSampleSentence(alignment[0], options.answer),
				Utils: Utils
			}));

			var that = this;

			return this;
		},
		checkAnswer: function(e) {
			e.preventDefault();
			var attempt = $(e.target).find('input').val();
			var correct = attempt === this.model.get('value');

			var options = {
				'answer': correct ? 'correct' : 'incorrect'
			};

			this.render(options);

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
		renderAlignments: function(e) {
			/*this.$el.find('[data-toggle="morea"]').each(function(i, el) {
				new Morea(el, {
					mode: 'display',
					data: that.constructPhrase(phrase),
					targets: el.getAttribute('data-targets').split(','),
					langs: {
						"grc": {
							"hr": "Greek",
							"resource_uri": "",
							"dir": "ltr"
						},
						"en": {
							"hr": "English",
							"resource_uri": "",
							"dir": "ltr"
						}
					}
				});
			});*/
		},
		renderParseTree: function(e) {
			/*this.$el.find('[data-toggle="daphne"]').each(function(i, el) {
				new Daphne(el, {
					data: phrase,
					mode: 'edit',
					width: el.getAttribute('data-width') || 200,
					height: 400,
					initialScale: 0.9
				});
			});*/

		}
	});
	return View;
});
