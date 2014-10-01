define(['jquery', 'underscore', 'backbone', 'models', 'collections', 'utils', 'text!/templates/js/microlesson.html'], function($, _, Backbone, Models, Collections, Utils, Template) { 

	var View = Backbone.View.extend({
		events: {
			'click .corner.right a': 'skipQuestion'
		},
		template: _.template(Template),
		initialize: function(options) {

			var that = this;
			this.options = options;

			// Instantiate our collection, tell it how to populate vocabulary
			this.collection = new Collections.Words([], { grammar: options.ref });
			this.collection.on('populated', this.selectNext, this);
			this.collection.on('change:selected', this.render, this);
			this.collection.populateVocab();
		},
		selectNext: function() {
			// TODO: power this by api
			var oldModel = this.collection.findWhere({ selected: true });
			if (oldModel) oldModel.set('selected', false);
			this.model = this.collection.at(1);

			// if there is no model, because this unit doesn't have any
			if (this.model) this.model.set('selected', true);
			else this.render();
		},
		render: function() {
			this.$el.html(this.template({
				model: this.model
			}));	
			this.renderGrammar();
		},
		renderGrammar: function() {
			var el = this.$el.find('.study-notes');	

			if (el.find('div[data-url]').length !== 0) {
				el.show();
				return;
			}

			var that = this;
			var topics = Utils.getHTMLbySmyth(this.model.getGrammar() || this.options.ref);
			topics.forEach(function(topic) {
				var title = Utils.Smyth.filter(function(s) { return s.ref === topic.smyth })[0].title;
				el.find('.table-of-contents').append('<li><a href="#' + topic.ref + '">' + title + '</a></li>');
			});

			for (var i = 0, topic; topic = topics[i]; i++) {
				el.append('<div data-url="' + topic.includeHTML + '"></div>');	
				$.ajax({
					url: topic.includeHTML,
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
		selectModel: function() {

		},
		skipQuestion: function() {

		}
	});

	return View;
});
