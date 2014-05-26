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

			// Bind to our document model and our word collection
			this.model.on('populated', this.reRender, this);
			this.model.words.on('change:selected', this.toggleHighlight, this); 

			if (this.options.CTS == undefined) {
				this.options.CTS = this.model.words.at(0).get('sentenceCTS');
			}

			this.model.populate(this.options.CTS);
		},
		render: function() {
			this.$el.html(this.template({ 
				side: this.options.side, 
				author: this.model.get('author'),
				work: this.model.get('name'),
				lang: this.model.get('lang'),
				words: {},
				cts: this.options.CTS
			})); 
			return this;
		},
		reRender: function(model) {

			this.$el.html(this.template({ 
				side: this.options.side, 
				author: this.model.get('author'),
				work: this.model.get('name'),
				lang: this.model.get('lang'),
				words: this.model.words.models,
				cts: this.options.CTS
			})); 

			// Update the 'next or previous' page links
			var that = this;
			this.$el.find('a').attr('href', function() {
				var cts = that.options.side == 'left' ? that.model.getPrevCTS(that.options.CTS) : that.model.getNextCTS(that.options.CTS); 
				return '/reader/' + (cts || '');
			}).tooltip();

			var ref = this.options.CTS.split(':');
			this.$el.find('h1 a').html(ref[ref.length-1]);

			return this;	
		},
		turnPage: function(e) {
			if (e) e.preventDefault();
			Backbone.history.navigate(this.$el.find('.corner a').attr('href'), { trigger: true });		
		},
		turnToPage: function(CTS) {
			this.options.CTS = CTS;
			this.model.populate(CTS);
		},
		hoverWord: function(e) {
			var word = this.model.words.findWhere({ 
				wordCTS: $(e.target).attr('data-cts') 
			});

			var hovered = (e.type == 'mouseenter') ? true : false;
			word.set('hovered', hovered);
		},
		clickWord: function(e) {
			// See if any word is previously selected
			var prev = this.model.words.findWhere({
				selected: true
			});
			var target = this.model.words.findWhere({ 
				wordCTS: $(e.target).attr('data-cts') 
			});

			// If this word is the same as current word, deselect
			if (target == prev) {
				prev.set('selected', false);
				this.$el.parent().css('padding-bottom', '80px');
			}
			else if (typeof(prev) != 'undefined') {
				prev.set('selected', false);
				target.set('selected', true);
				this.$el.parent().css('padding-bottom', '200px');
			}
			else {
				target.set('selected', true);
				this.$el.parent().css('padding-bottom', '200px');
			}
		},
		// If an element becomes selected or de-selected, update highlight accordingly
		toggleHighlight: function(model) {
			if (model.get('selected'))
				this.$el.find('.page-content span[data-cts="' + model.get('wordCTS') + '"]')
					.addClass('selected');
			else if (!model.get('selected'))
				this.$el.find('.page-content span[data-cts="' + model.get('wordCTS') + '"]')
					.removeClass('selected');
		}
	});

	return View;
});
