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
			sendSubmission: function(submission) {
				var data = {
					// String representation of the user's response
					response: submission.response,

					// Name of the task, including args
					task: submission.task,

					// Number between 0-1
					accuracy: submission.accuracy,

					// Array of CTS ids
					encounteredWords: submission.encounteredWords || [],

					// Accessible from topic modal as topic.get('ref')
					ref: submission.ref,

					// Timestamp is now
					timestamp: submission.timestamp || (new Date()).toISOString(),
					starttime: submission.starttime
				};

				// Send to server
				$.ajax({
					url: '/api/v1/submission/',
					headers: {
						'X-CSRFToken': CSRF_TOKEN
					},
					data: JSON.stringify(data),
					processData: false,
					dataType: 'json',
					contentType: 'application/json',
					type: 'POST',
					success: function(response) {
						console.log("Successful data submission!");

						// Here, send a trigger to the parent view (tasks.js) about the state
					},
					error: function(x, y, z) {
						var title = 'An error occured';
						var msg = 'Trouble communicating with the server. Please refresh the page and try again.';
						var options = { state: 'ok' };
						Utils.displayNotification(title, msg, options);
					}
				});
			},
			getNewState: function(answer, userInput) {
				// Return a state based on edit distance
				var distance = Utils.lDistance(answer, userInput);
				
				if (distance == 0)
					return 'success';
				
				if (distance > answer.length)
					return 'error';

				return 'warning';
			},
			getAccuracy: function(a, b) {
				/* If you want to do any pre-processing before we compare user answers,
				 * do this in the subtask. e.g. if you don't want the diacritics to count
				 * against the user, convert them using Utils.removeDiacritics before using
				 * this function.
				 */

				 return Utils.compareStrings(a, b);
			}
		});
	}
);
