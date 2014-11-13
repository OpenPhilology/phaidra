define(['jquery', 
	'underscore', 
	'backbone', 
	'models/word', 
	'collections/words', 
	'utils', 
	'typegeek',
	'text!/templates/js/lessons/tasks/translate_word.html'], 
	function($, _, Backbone, WordModel, WordsCollection, Utils, TypeGeek, Template) {

		return Backbone.View.extend({
			template: _.template(Template),
			tagName: 'div',
			className: 'subtask',
			initialize: function(options) {
				this.options = options;
				var that = this;
				
				// Fetch the sentence our model is in, then render
				this.collection.url = this.model.get('sentence_resource_uri') + '?full=True';
				this.collection.fetch({
					remove: false,
					merge: true,
					success: that.fullRender.bind(that)
				});
			},
			render: function() {
				// Initial render just to make $el available to parent view
				return this;
			},
			fullRender: function() {

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

				this.$el.html(this.template({
					model: this.model,
					definition: this.defs,
					sentence: this.makeSampleSentence(alignments[0], 'open'),
					translated_sentence: translation
				}));

				new TypeGeek(this.$el.find('input[type="text"]')[0]);

				this.$el.find('[data-toggle="tooltip"]').tooltip();
			},
			makeSampleSentence: function(sentence, state) {
				// State: open, correct, incorrect
				state = state || 'open';

				return _.map(sentence.words, function(s) {
					if (state === 'open')
						return s.value === this.model.get('value') ? new Array(s.value.length + 1).join('_') : s.value;
					else if (state === 'correct')
						return s.value === this.model.get('value') ? ('<span class="correct">' + s.value + '</span>') : s.value;
					else if (state === 'incorrect')
						return s.value === this.model.get('value') ? ('<span class="incorrect">' + s.value + '</span>') : s.value;
				}.bind(this)).join(' &nbsp; ');
			}
		});
	}
);
