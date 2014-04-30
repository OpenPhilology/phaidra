define(['jquery', 'underscore', 'backbone', 'text!templates/notes.html'], function($, _, Backbone, NotesTemplate) { 

	var View = Backbone.View.extend({
		tagName: 'div', 
		className: 'col-md-12 notes',
		template: _.template(NotesTemplate),
		events: { },
		initialize: function(options) {
			this.options = options;	
			this.collection.bind('change', this.updateDisplay, this);
		},
		render: function() {
			this.$el.html(this.template());
			return this;	
		},
		/*
		*	Currently just changes which word is displayed in notes section. Will have support for:
		*		- Viewing existing annotations for this word (and its containing sentence, and section)
		*
		*	TODO: Clean this up & modularize!
		*/
		updateDisplay: function(model) {
			if (model.get('hovered') && !model.get('selected') && (this.collection.findWhere({ selected: true }) == undefined)) {
				this.$el.find('p').html('Information about <span lang="' + model.get('lang') +'">' + model.get('value') + '</span>');
				this.$el.animate({
					height: '60px'
				}, 200, "linear");
			}

			// This will perform a fetch on the model for full data
			else if (model.get('selected')) {
				this.$el.animate({
					height: '200px'
				}, 200, "linear");
				
				this.$el.find('p').html(function() {
					var content = '<span lang="' + model.get('lang') + '">' + model.get('value') + '</span>';
					content += '<p>CTS: ' + model.get('CTS') + '</p>';
					return content;
				});
			}
		}
	});

	return View;

});
