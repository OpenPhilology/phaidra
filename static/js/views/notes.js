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
		updateDisplay: function(model) {
			this.$el.find('p').html('Information about <span lang="grc">' + model.get('value') + '</span>');
		}
	});

	return View;

});
