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

			this.collection.on('populated', this.reRender, this);
			this.collection.on('change:selected', this.toggleHighlight, this); 
			
			var word = this.collection.findWhere(
				{ sentence_resource_uri: options.sentence_resource_uri }
			);
			
			if (word)
				this.options.CTS = word.get('sentenceCTS');
			else {
				this.collection.addSentence({ sentence_resource_uri: this.options.sentence_resource_uri });
			}

		},
		render: function() {
			return this;
		},
		reRender: function() {
			console.log("rerender called");
			
			// Get the new corresponding CTS
			this.options.CTS = this.collection.findWhere(
				{ sentence_resource_uri: this.options.sentence_resource_uri }
			).get('sentenceCTS');

			var that = this;

			// Pass in CTS of sentence so only words in that sentence appear on this page  
			this.$el.html(this.template({ 
				side: this.options.side, 
				author: this.collection._meta.author,
				work: this.collection._meta.name,
				lang: this.collection._meta.lang,
				words: this.collection.models,
				cts: this.options.CTS
			})); 

			// Update the 'next or previous' page links
			var model = this.collection.findWhere({ sentenceCTS: this.options.CTS });
			/*this.$el.find('a').attr('href', function() {
				var cts = that.options.side == 'left' ? model.get('prevPageCTS') : model.get('nextPageCTS'); 
				return '/reader/' + (cts || '');
			}).tooltip();*/

			var ref = this.options.CTS.split(':');
			this.$el.find('h1 a').html(ref[ref.length-1]);

			return this;	
		},
		turnToPage: function(cts) {
			this.options.CTS = cts;
			this.collection.addSentence({ sentenceCTS: this.options.CTS });
			this.reRender();
		},
		turnPage: function(e) {
			e.preventDefault();
			Backbone.history.navigate(this.$el.find('.corner a').attr('href'), { trigger: true });		
		},

		// TODO: Delegate these responsibilities to a super tiny word view 

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
			else if (!model.get('selected'))
				this.$el.find('.page-content span[data-cts="' + model.get('CTS') + '"]')
					.removeClass('selected');
		}
	});

	return View;
});
