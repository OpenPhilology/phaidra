define(['jquery', 'underscore', 'backbone', 'collections', 'text!templates/aligner.html'], function($, _, Backbone, Collections, AlignerTemplate) { 

	var View = Backbone.View.extend({
		events: { },
		tagName: 'div',
		className: 'aligner',
		template: _.template(AlignerTemplate),
		initialize: function(options) {
			this.options = options;

			if (!options.CTS)
				this.options.CTS = 'urn:cts:greekLit:tlg0003.tlg001.perseus-grc1:1.89.1';

			// Fetch Document and get our CTS of interest (for read mode)
			this.documents = new Collections.Documents();
			this.documents.on('add', this.initializeAligner, this);
			this.documents.fetch();

			// Bind view context to our model population callbacks
			_.bindAll(this, "fetchSuccess", "fetchError");

			/* Options.mode:
				* create: input your own translation
				* complete: align to existing translation (answer checking)
				* edit: edit an existing translation
				* read: read-only using existing alignment data
			*/
		},
		render: function() {
			return this;	
		},
		renderAlignment: function(model) {
			var that = this;

			/* Aggregate the alignment data
			var sentence = model.find({ sentenceCTS: this.option.CTS });
			var 
			for (var i = 0; i < sentence.length; i++) {
				
			}*/

			this.$el.html(this.template({
				words: model.words.models,
				doc: model.attributes,
				CTS: that.options.CTS 
			}));
		},
		initializeAligner: function(model) {
			if (model.get('lang') == 'grc') {
				this.model = model;
				this.model.fetch({
					success: this.fetchSuccess,
					error: this.fetchError
				});
			}
		},
		fetchSuccess: function(model, options) {
			// If we're successful at this point, then we decide what to do with the data
			model.on('populated', this.renderAlignment, this);
			model.populate(this.options.CTS);
		},
		fetchError: function(model, options) {
			console.log("error fetching ", model);
		}
	});

	return View;
});
