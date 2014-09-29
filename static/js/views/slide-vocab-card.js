define(['jquery', 'underscore', 'backbone', 'models', 'collections', 'text!/templates/js/slide-vocab-card.html', 'morea', 'daphne', 'utils'], function($, _, Backbone, Models, Collections, Template, Morea, Daphne, Utils) {
	var View = Backbone.View.extend({
		events: { 
			'submit form': 'checkAnswer',
			'click .nav-tabs a': 'toggleNotes'
		},
		template: _.template(Template),
		initialize: function(options) {
			this.model.on('change:populated', this.render, this);
			this.model.fetchSentence(this.model.get('CTS'));
		},
		render: function(options) {
			this.phrase = this.model.getPhrase();
			this.defs = this.model.getDefinition();

			// TODO: Deal with defaults
			if (!options) {
				var options = {}; 
				options.answer = 'open';
			}
			
			// If our data's fucked, don't bother
			if (!this.phrase || !this.defs) {
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

			var alignment = this.constructPhrase(this.phrase);

			this.$el.html(this.template({
				model: this.model,
				defs: this.defs,
				options: options,
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
			var that = this;
			this.$el.find('[data-toggle="morea"]').each(function(i, el) {
				new Morea(el, {
					mode: 'display',
					data: that.constructPhrase(that.phrase),
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
			});
			this.$el.find('.vocab-notes div[data-source="alignment"]').show();
		},
		renderParseTree: function(e) {
			var that = this;
			this.$el.find('[data-toggle="daphne"]').each(function(i, el) {
				new Daphne(el, {
					data: that.phrase,
					mode: 'edit',
					width: el.getAttribute('data-width') || 200,
					height: 400,
					initialScale: 0.9
				});
			});
			this.$el.find('.vocab-notes div[data-source="parse-tree"]').show();
		},
		renderGrammar: function() {
			var el = this.$el.find('.vocab-notes div[data-source="grammar"]');	

			if (el.children().length !== 0) {
				el.show();
				return;
			}

			var that = this;
			var urls = Utils.getHTMLbySmyth(this.model.getGrammar().reverse());

			for (var i = 0, url; url = urls[i]; i++) {
				el.append('<div data-url="' + url + '"></div>');	
				$.ajax({
					url: url,
					dataType: 'text',
					success: function(response) {
						that.$el.find('div[data-url="' + this.url + '"]').append(response + '<hr>');
					},
					error: function(x, y, z) {
						console.log(x, y, z);
					}
				});
			}

			el.show();
		},
		toggleNotes: function(e) {
			e.preventDefault();
			var target = e.target.dataset.target;

			// First see if they want to de-toggle
			if ($(e.target).hasClass('active')) {
				$(e.target).removeClass('active'); 
				this.$el.find('.vocab-notes div[data-source="' + target + '"]').hide();
				return;
			}

			// Otherwise, find the correct note to show
			this.$el.find('.vocab-notes[data-source]').hide();
			this.$el.find('.nav li').removeClass('active');
			this.$el.find('.nav a[data-target="' + target + '"]').parent().addClass('active');

			if (target === 'alignment') this.renderAlignments();
			else if (target === 'parse-tree') this.renderParseTree();
			else if (target === 'grammar') this.renderGrammar();
		}
	});
	return View;
});
