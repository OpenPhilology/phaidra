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
			this.$el.html(this.template({
				model: this.model
			}));

			this.$el.find('.card').each(function(i, el) {
				if (!this.cards[el.dataset.lemma])  
					this.cards[el.dataset.lemma] = new VocabCardView({ collection: this.model.get('vocab'), el: el }); 
				else 
					this.cards[el.dataset.lemma].render();
			}.bind(this));
			
			return this;
		}
	});

	return View;
});
