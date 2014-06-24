define(['jquery', 'underscore', 'backbone', 'models', 'collections', 'text!templates/slide-multicomp.html'], function($, _, Backbone, Models, Collections, Template) {
	var View = Backbone.View.extend({
		tagName: 'div',
		className: 'slide-unit',
		template: _.template(Template),
		events: {
			"click .options a" : "selectAnswer",
			"click .answers a" : "deselectAnswer"
		},
		initialize: function(options) {
			this.options = options;

			// Decide whether we can draw right away or must wait
			if (this.model.get('populated'))
				this.draw();
			else
				this.model.on('populated', this.draw, this);
		},
		render: function() {
			return this;	
		},
		draw: function() {
			this.$el.html(this.template(this.model.attributes));
		},
		selectAnswer: function(e) {
			e.preventDefault();

			var selectedOption = $(e.target);
			if (e.target.tagName === 'SPAN')
				selectedOption = selectedOption.parent().parent();
			else if (e.target.tagName === 'A')
				selectedOption = selectedOption.parent();

			var answer = selectedOption.clone();

			answer.data('source', selectedOption);

			this.$el.find('ul.answers').append(answer);
			selectedOption.hide();

			// Check answer, if appropriate

			if (this.$el.find('ul.answers li').length == this.model.get('answers').length) {
				var attempt = [];
				var btns = this.$el.find('ul.answers li a');
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

				// Display correct answer message
				var info = this.$el.find('.slide-feedback');
				info.html(this.model.get('successMsg'));
				info.removeClass('bg-info');
				info.addClass('bg-success');
				info.slideDown();
			}
			else {

				// Give the user a hint so they can try again
				var info = this.$el.find('.slide-feedback');
				info.html(this.model.get('hintMsg'));
				info.removeClass('bg-success');
				info.addClass('bg-info');
				info.slideDown();
			}
		}
	});

	return View;
});
