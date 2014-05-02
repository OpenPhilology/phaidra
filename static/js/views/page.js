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

			return this;	
		},
		turnPage: function(cts) {
			var that = this;

			// Let's start at the very beginning, a very good place to staaaart!
			if (typeof(cts) == 'undefined')
				cts = 'urn:cts:greekLit:tlg0003.tlg001.perseus-grc1:1.89.1';

			$.ajax({
				url: '/api/v1/sentence/?format=json&CTS=' + cts,
				dataType: 'json',
				success: function(response) {
					var text = that.prepText(response.objects[0]);
					var ref = response.objects[0]["CTS"].split(':');

					that.$el.find('h1 a').html(ref[ref.length-1]);
				},
				error: function() {
					that.$el.find('.page-content').html('Error was encountered trying to render this page.');
				}
			});
		},
		/*
		* Builds up our collection of words for this page 
		*/
		prepText: function(text) {
			var that = this;
			var tokens = $.trim(text.sentence).split(' ');

			$.each(tokens, function(i, token) {
				that.collection.add({
					'value': token,
					'lang': 'grc',
					'CTS': text.CTS + ':' + (i + 1)
				});
			});

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
				this.$el.parent().css('padding-bottom', '0');
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
