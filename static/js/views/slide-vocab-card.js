define(['jquery', 'underscore', 'backbone', 'models', 'collections', 'text!/templates/js/slide-vocab-card.html', 'morea', 'daphne'], function($, _, Backbone, Models, Collections, Template, Morea, Daphne) {
	var View = Backbone.View.extend({
		events: { },
		template: _.template(Template),
		initialize: function(options) {
			this.model = this.collection.findWhere({ lemma: this.el.dataset.lemma });
			this.model.on('change:populated', this.render, this);
			this.model.fetchSentence(this.model.get('CTS'));
		},
		render: function() {
			var phrase = this.model.getPhrase();
			
			// If our data's fucked, don't bother
			if (!phrase) {
				this.remove();
				return;
			}

			this.$el.html(this.template({
				model: this.model
			}));

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
				alignment.translations = i === 0 ? { 'en': '/' } : { 'grc': '/' }; 
				alignment.CTS = s[0].CTS.split(':').slice(0, 5).join(':');
				return alignment;
			});

			/*this.$el.find('[data-toggle="daphne"]').each(function(i, el) {
				new Daphne(el, {
					data: phrase,
					mode: 'edit',
					width: el.getAttribute('data-width') || 200,
					height: 400,
					initialScale: 0.9
				});
			});*/

			this.$el.find('[data-toggle="morea"]').each(function(i, el) {
				new Morea(el, {
					mode: 'display',
					data: alignments,
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

			return this;
		}
	});
	return View;
});
