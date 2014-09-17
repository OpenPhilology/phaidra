define(['jquery', 'underscore', 'backbone', 'models', 'collections', 'text!/templates/js/slide-directselect.html'], function($, _, Backbone, Models, Collections, Template) {
	var View = Backbone.View.extend({
		tagName: 'div',
		className: 'slide-unit',
		template: _.template(Template),
		events: {
			"click .direct-select a" : "selectAnswer",
		},
		initialize: function(options) {
			this.options = options;
			this.model.on('change:populated', this.render, this);
		},
		render: function() {
			this.$el.html(this.template(this.model.attributes));
			return this;	
		},
		selectAnswer: function(e) {
			e.preventDefault();
			this.model.set('starttime', new Date(this.$el.data('starttime')));

			if (this.finished)
				return false;

			var selectedOption = $(e.target);
			if (e.target.tagName === "SPAN")
				selectedOption = selectedOption.parent();

			selectedOption.addClass('selected');

			// Check answer, if appropriate

			if (this.$el.find('.direct-select a.selected').length == this.model.get('answers').length) {
				var attempt = [];
				var btns = this.$el.find('.direct-select a.selected');
				for (var i = 0; i < btns.length; i++)
					attempt.push(btns[i].getAttribute('data-value'))

				this.checkAnswer(attempt);
			}
		},
		deselectAnswer: function(e) {
			e.preventDefault();

			var answer = $(e.target).parent();
			answer.hide();

			answer.data('source').show();
			answer.remove();
		},
		checkAnswer: function(attempt) {
			if (this.model.checkAnswer(attempt)) {

				this.$el.find('.selected').removeClass('selected').addClass('success');

				// Display correct answer message
				var info = this.$el.find('.slide-feedback');
				info.html(this.model.get('successMsg'));
				info.removeClass('bg-info');
				info.addClass('bg-success');
				info.slideDown();

			}
			else {

				this.$el.find('.selected').removeClass('selected').addClass('failure');

				// Give the user a hint so they can try again
				var info = this.$el.find('.slide-feedback');
				info.html(this.model.get('hintMsg'));
				info.removeClass('bg-info');
				info.addClass('bg-error');
				info.slideDown();

			}

			// Prevent user from continuing to click
			this.finished = true;
		}
	});

	return View;
});
