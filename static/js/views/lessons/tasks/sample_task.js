define(['jquery', 
	'underscore', 
	'backbone', 
	'views/lessons/tasks/base_task',
	'utils',
	'typegeek',
	'text!/templates/js/lessons/tasks/sample_task.html'], 
	function($, _, Backbone, BaseTaskView, Utils, TypeGeek, Template) {

		return BaseTaskView.extend({
			template: _.template(Template),
			events: {
				'submit form': 'checkAnswer'
			},
			initialize: function(options) {
				console.log(options.args);
				BaseTaskView.prototype.initialize.apply(this, [options]);
			},

			// Initial render just to make $el available to parent view
			render: function() {
				return this;
			},

			// Called when the sentence is populated
			fullRender: function(options) {

				options = options || {};
				options.state = options.state || 'open';

				this.$el.html(this.template({
					model: this.model,
					options: options
				}));
				
				// Now that the DOM is available, bindings:
				var answerBox = this.$el.find('input[type="text"]')[0];
				new TypeGeek(answerBox);
				answerBox.focus();
			},
			checkAnswer: function(e) {
				e.preventDefault();

				// Grab answers from the UI, pass to base_task
				var inputField = $(e.target).find('input');
				var answer = this.model.get('value');
				var userAnswer = inputField.val();

				// Call our BaseTask's answer checking functionality 
				var newState = BaseTaskView.prototype.checkAnswer.apply(this, [answer, userAnswer]);

				// Update our UI accordingly
				this.fullRender({ state: newState });
			}
		});
	}
);
