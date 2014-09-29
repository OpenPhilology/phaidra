define(['jquery', 'underscore', 'backbone', 'models', 'collections', 'views/slide-vocab-card', 'text!/templates/js/slide-vocab.html'], function($, _, Backbone, Models, Collections, VocabCardView, Template) {
	var View = Backbone.View.extend({
		tagName: 'div',
		className: 'slide-unit',
		template: _.template(Template),
		events: { },
		initialize: function(options) {
			this.options = options;
			this.cards = [];
			this.model.on('change:populated', this.render, this);
		},
		render: function() {
			this.model.get('vocab').on('change:active', this.flipCard, this);

			this.$el.html(this.template({
				model: this.model
			}));
			var vocab = this.model.get('vocab').filterVocabulary()[0];
			this.model.get('vocab').findWhere({ lemma: vocab }).set('active', true);

			return this;
		},
		flipCard: function(model) {
			var lemma = model.get('lemma');

			// Hide other cards
			this.$el.find('.card').each(function(i, el) {
				$(el).hide();
			}.bind(this));
			
			// Show this card
			var el = this.$el.find('.card[data-lemma="' + lemma + '"]')[0];

			if (!this.cards[el.dataset.lemma])
				this.cards[el.dataset.lemma] = new VocabCardView({ collection: this.model.get('vocab'), el: el, model: model }); 
			else 
				this.cards[el.dataset.lemma].render();
			
			this.cards[el.dataset.lemma].$el.show();
		}
	});

	return View;
});
