define(['jquery', 'underscore', 'backbone', 'models', 'collections'], function($, _, Backbone, Models, Collections) {
	var View = Backbone.View.extend({
		tagName: 'div',
		className: 'slide-unit',
		events: {
			"click .direct-select a" : "selectAnswer"
		},
		initialize: function(options) {
			this.$el.html(options.template(this.model.attributes));
		},
		render: function() {

			if (this.model.get('task')) {
				var div = this.$el.find('.responseText');
				div.html("");
				var words = this.model.get('responseText').words;
				var that = this;

				for (var i = 0; i < words.length; i++) {
					var text = words[i]["value"];
					var color = (words[i]["lemma"] == that.model.get('lemma')) ? '#EEE' : '#FFF'

					div.append('<div class="greek-text" style="display: inline-block; padding: 10px; background-color: ' + color + '">' + text + '</div> ');
				}
			}

			return this;	
		},
		selectAnswer: function(e) {
			e.preventDefault();

			if (this.finished)
				return false;

			var selectedOption = $(e.target);
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
				info.slideDown();
			}

			// Prevent user from continuing to click
			this.finished = true;
		}
	});

	return View;
});
