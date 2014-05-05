define(['jquery', 'underscore', 'backbone', 'text!templates/notes.html'], function($, _, Backbone, NotesTemplate) { 

	var View = Backbone.View.extend({
		tagName: 'div', 
		className: 'col-md-12 notes',
		template: _.template(NotesTemplate),
		events: { 
			'click a > .glyphicon-chevron-up': 'collapseNotes'
		},
		initialize: function(options) {
			this.options = options;	
			this.collection.bind('change:selected change:hovered', this.toggleNotes, this);
			this.collection.on('populated', this.renderDetails, this);
		},
		render: function() {
			this.$el.html(this.template());
			this.$el.find('.notes-nav a').tooltip({ container: 'body' });
			return this;	
		},
		renderDetails: function() {
			this.$el.addClass('expanded');
			var selected = this.collection.findWhere({ selected: true });
			this.$el.find('h3').html(function() {
				var content = '<span lang="grc">' + selected.get('value') + '</span>';
				content += ' <small>comes from <strong lang="grc">' + selected.get('lemma') + '</strong>';
				return content;
			});
		},
		toggleNotes: function(model) {
			if (model.get('hovered') && !model.get('selected') && (this.collection.findWhere({ selected: true }) == undefined)) {
				this.$el.find('.intro').html(
					'Information about <span lang="' + model.get('lang') +'">' + model.get('value') + '</span>'
				);
				this.$el.removeClass('expanded');
				this.$el.find('.notes-nav a').eq(1).attr('title', 'Hide Resources');
			}

			// This will perform a fetch on the model for full data
			else if (model.get('selected')) {
				this.$el.find('.intro').html("Loading");
				this.$el.find('.notes-nav a').eq(1).attr('title', 'Show Resources');
				this.collection.populate(model.get('sentenceURI'));
			}

		},
		collapseNotes: function(e) {
			e.preventDefault();
			var selected = this.collection.findWhere({ selected: true });
			if (typeof(selected) != 'undefined')
				selected.set('selected', false);
		}
	});

	return View;

});
