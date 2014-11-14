define(['jquery', 
	'underscore',
	'backbone',
	'utils'],
	function($, _, Backbone, Utils) {
		
		return Backbone.View.extend({
			tagName: 'div',
			className: 'subtask',
			initialize: function(options) {
				this.options = options;

				var that = this;
				// By default, fetch the sentence our model is in, then render
				this.collection.url = this.model.get('sentence_resource_uri') + '?full=True';
				this.collection.fetch({
					remove: false,
					merge: true,
					success: that.fullRender.bind(that)
				});
			},
			render: function() {
				return this;
			},
			fullRender: function() {
				return this;
			},
			sendSubmission: function(answer, accuracy, startTime, words) {
				var data = {

				};

				// Send to server
			},
			checkAnswer: function(answer, userInput) {
				// Return a state based on edit distance
				var distance = Utils.lDistance(answer, userInput);
				
				if (distance == 0)
					return 'success';
				
				if (distance > answer.length)
					return 'error';

				return 'warning';
			}
		});
	}
);
