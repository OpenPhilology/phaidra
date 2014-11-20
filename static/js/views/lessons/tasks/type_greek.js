define(['jquery', 
	'underscore', 
	'backbone', 
	'views/lessons/tasks/base',
	'utils',
	'typegeek',
	'text!/templates/js/lessons/tasks/type_greek.html'], 
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

				// Pull up the definition
				//this.phrase = this.collection.buildPhrase(this.model);
				this.definition = this.model.getDefinition(LOCALE);

				// If we can't get a definition, remove this view and return false
				// So the parent view can build a new, better view!
				if (!this.definition) {
					this.remove();
					return false;
				}

				this.$el.html(this.template({
					model: this.model,
					options: options,
					definition: this.definition,
					Utils: Utils
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
				var answer = Utils.romanize(this.model.get('value'));
				var userAnswer = Utils.romanize(inputField.val());

				console.log(answer, userAnswer);

				// Call our BaseTask's answer checking functionality 
				var newState = BaseTaskView.prototype.getState.apply(this, [answer, userAnswer]);

				// Update our UI accordingly
				this.fullRender({ state: newState });
			}
		});
	}
);
