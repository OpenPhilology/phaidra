define(['jquery', 'underscore', 'backbone', 'text!templates/page.html'], function($, _, Backbone, PageTemplate) { 

	var View = Backbone.View.extend({
		events: { 
			'click .corner a': 'turnPage',
			'mouseenter .page-content span': 'hoverWord',
			'mouseleave .page-content span': 'hoverWord',
			'click .page-content span': 'clickWord'
		},
		tagName: 'div',
		className: 'col-md-6',
		template: _.template(PageTemplate),
		initialize: function(options) {
			this.options = options;
			this.render();
			this.turnPage(options.cts);

			this.collection.on('change:selected', this.toggleHighlight, this); 
		},
		render: function() {
			// Pass in CTS of sentence so only words in that sentence appear on this page  
			this.$el.html(this.template({ 
				side: this.options.side, 
				words: this.collection.models,
				cts: this.options.cts
			})); 
			this.$el.find('a[data-toggle="tooltip"]').tooltip({ container: 'body' });

			var ref = this.options.cts.split(':');
			this.$el.find('h1 a').html(ref[ref.length-1]);

			return this;	
		},
		turnPage: function(cts) {
			this.cts = cts;
			this.render();
		},

		// TODO: Delegate these responsibilities to a super tiny word view 

		/*
		*	Change the 'hover' state of the model appropriately.
		*/
		hoverWord: function(e) {
			var model = this.collection.findWhere({ 
				CTS: $(e.target).attr('data-cts') 
			});

			var hovered = (e.type == 'mouseenter') ? true : false;
			model.set('hovered', hovered);
		},
		clickWord: function(e) {
			// See if any word is previously selected
			var prev = this.collection.findWhere({
				selected: true
			});
			var model = this.collection.findWhere({ 
				CTS: $(e.target).attr('data-cts') 
			});

			// If this word is the same as current word, deselect
			if (model == prev) {
				prev.set('selected', false);
				this.$el.parent().css('padding-bottom', '80px');
			}
			else if (typeof(prev) != 'undefined') {
				prev.set('selected', false);
				model.set('selected', true);
				this.$el.parent().css('padding-bottom', '200px');
			}
			else {
				model.set('selected', true);
				this.$el.parent().css('padding-bottom', '200px');
			}
		},
		// If an element becomes selected or de-selected, update highlight accordingly
		toggleHighlight: function(model) {
			if (model.get('selected'))
				this.$el.find('.page-content span[data-cts="' + model.get('CTS') + '"]')
					.addClass('selected');
			else if (!model.get('selected')) {
				this.$el.find('.page-content span[data-cts="' + model.get('CTS') + '"]')
					.removeClass('selected');
			}
		}
	});

	return View;
});
