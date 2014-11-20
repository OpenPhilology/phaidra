define(['jquery', 
	'underscore', 
	'backbone', 
	'views/lessons/tasks/base',
	'utils', 
	'typegeek',
	'text!/templates/js/lessons/tasks/translate_word.html'], 
	function($, _, Backbone, BaseTaskView, Utils, TypeGeek, Template) {

		return BaseTaskView.extend({
			template: _.template(Template),
			events: {
				'submit form': 'checkAnswer'
			},
			initialize: function(options) {
				BaseTaskView.prototype.initialize.apply(this, [options]);
			},
			render: function() {
				// Initial render just to make $el available to parent view
				return this;
			},
			fullRender: function(options) {
				
				options = options || {};
				options.state = options.state || 'open';

				this.phrase = this.collection.buildPhrase(this.model);
				this.defs = this.model.getDefinition(LOCALE);

				// !!!!! IMPORTANT !!!!!
				// Here we determine if a phrase can be made from our starter word.
				// If we cannot, then we must select a new model within the collection and destroy this view

				if (!this.phrase || !this.defs) {
					this.remove();
					return false;
				}

				var alignments = this.collection.buildAlignmentPhrase(this.phrase, LOCALE);
				var translation = this.collection.getTranslatedSentence(alignments, LOCALE);

				// Populate template with textual data
				this.$el.html(this.template({
					model: this.model,
					definition: this.defs,
					sentence: this.makeSampleSentence(alignments[0], options.state),
					translated_sentence: translation,
					options: options
				}));

				// Make it possible to type greek in the textarea
				var answerBox = this.$el.find('input[type="text"]')[0];
				new TypeGeek(answerBox);
				answerBox.focus();

				this.$el.find('[data-toggle="tooltip"]').tooltip();
			},
			makeSampleSentence: function(sentence, state) {
				// State: open, correct, incorrect
				state = state || 'open';

				return _.map(sentence.words, function(s) {
					if (state === 'open')
						return s.value === this.model.get('value') ? new Array(s.value.length + 1).join('_') : s.value;
					else if (state === 'success')
						return s.value === this.model.get('value') ? ('<span class="success">' + s.value + '</span>') : s.value;
					else if (state === 'warning')
						return s.value === this.model.get('value') ? ('<span class="warning">' + s.value + '</span>') : s.value;
					else if (state === 'error')
						return s.value === this.model.get('value') ? ('<span class="error">' + s.value + '</span>') : s.value;
				}.bind(this)).join(' &nbsp; ');
			},
			checkAnswer: function(e) {
				e.preventDefault();

				// Grab answers from the UI, pass to base_task
				var inputField = $(e.target).find('input');
				var answer = this.model.get('value');
				var userAnswer = inputField.val();

				// Call our BaseTask's answer checking functionality 
				var newState = BaseTaskView.prototype.getState.apply(this, [answer, userAnswer]);

				// Update our UI accordingly
				this.fullRender({ state: newState });
			}
		});
	}
);
