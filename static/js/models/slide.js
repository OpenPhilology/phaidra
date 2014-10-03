define(['jquery', 'underscore', 'backbone', 'utils'], function($, _, Backbone, Utils) {
	var Slide = {};

	Slide = Backbone.Model.extend({
		initialize: function() {
			_.bindAll(this, 'checkAnswer');
		},
		constructor: function(attributes, options) {
			Backbone.Model.prototype.constructor.call(this, attributes);

			this.collection = options.collection;
			this.options = options;
			this.attributes = attributes;
		},
		defaults: {
			'modelName': 'slide',
		},
		// TODO: Refactor this
		populate: function(options) {
			if (this.get('populated')) {
				if (options && options.success) options.success();
				return;
			}

			// Allows us to lazy-load everything
			if (this.get('includeHTML'))
				this.fetchHTML(options);
			else if (this.get('task'))
				this.fillAttributes(options);
			else if (this.get('type') !== 'slide_vocab') {
				this.set('populated', true);
				if (options && options.success) options.success();
			}
			else if (this.get('type') === 'slide_vocab') {
				if (this.collection.meta('vocab').meta('populated')) {
					if (options && options.success) options.success();
				}
				else {
					this.collection.meta('vocab').on('populated', options.success, this);
				}
			}
		},
		fetchHTML: function(options) {
			var that = this;
			if (this.get('content')) {
				this.set('populated', true);
				if (options && options.success) options.success();

				return;
			}

			// Fetch HTML if needed
			$.ajax({
				url: that.get('includeHTML'),
				dataType: 'text',
				success: function(response) {
					that.set('content', response);
					that.set('populated', true);
					if (options && options.success) options.success();
				},
				error: function(x, y, z) {
					if (options && options.error) options.error();
					console.log(x, y, z);
				}
			});
		},
		fillAttributes: function(options) {
			var that = this;
			var s = this.get('smyth');
			var entry = Utils.Smyth[s];

			// This differs based on if they loaded an exercise slide first, or started at beginning
			function useVocab() {
				if (!entry)
					return;
					
				var vocab = that.collection.meta('vocab');
				var candidates = vocab.filterVocabulary();
				that.collection.meta('vocab').meta('candidates', candidates);

				// Pick an example based on vocab for this unit
				var chosen = _.shuffle(_.filter(vocab.models, function(v) {
					return candidates.indexOf(v.get('lemma')) !== -1;
				})).splice(0, 1)[0];

				that.set('answers', [chosen.get(that.get('answerField'))]);
				that.set('encounteredWords', [chosen.get('CTS')]);

				// Treat question like template string to splice in value
				var data = {};
				data[that.get('endpoint')] = chosen.get('value');
				var compiled = _.template(that.get('question'));

				that.set('question', compiled(data));
				that.set('populated', true);
				if (options && options.success) options.success();
			}
			useVocab.bind(this);

			if (this.collection.meta('vocab').meta('populated'))
				useVocab();
			else
				this.collection.meta('vocab').on('populated', useVocab, this);

		},
		checkAnswer: function(attempt) {

			if (this.get('type') === 'slide_direct_select') {
				var correct = true;

				if (typeof(attempt) == 'string')
					attempt = [attempt]

				// Check if all submitted attempts are somewhere in answers
				if (this.get('require_all').toString() === "false") {
					for (var i = 0; i < attempt.length; i++)
						if (this.get('answers').indexOf(attempt[i]) == -1)
							correct = false;

					correct = correct ? true: false;
				}
				// Require order implies that require_all is also true
				else if (this.get('require_order').toString() === "true") {
					if (this.get('answers').length !== attempt.length)
						correct = false;
					else {
						for (var i = 0; i < attempt.length; i++) {
							if (attempt[i] != this.get('answers')[i]) 
								correct = false;
						}

						correct = correct ? true : false;
					}
				}
				// All Required, but order is not required
				else if (this.get('require_all').toString() === "true" && this.get('require_order').toString() === "false")
					correct = $(attempt).not(this.get('answers')).length == 0 && $(this.get('answers')).not(attempt).length == 0;
				else
					correct = false;

				this.set('accuracy', (correct ? 100 : 0));
			}
			else if (this.get('type') === 'slide_info') {
				// Means we are manually checking in either morea.js or daphne.js
				if (!attempt)
					attempt = this.get('response');
			}

			this.set('endtime', (new Date()));
			this.sendSubmission(attempt);

			return correct;
		},
		sendSubmission: function(attempt) {
			var data = {
				response: JSON.stringify(attempt),
				task: this.get('task') || 'static_exercise',
				accuracy: this.get('accuracy'),
				encounteredWords: this.get('encounteredWords'),
				slideType: this.get('type'),
				smyth: this.get('smyth') || undefined,
				timestamp: this.get('endtime').toISOString(),
				starttime: this.get('starttime').toISOString()
			};

			$.ajax({
				url: '/api/v1/submission/',
				headers: { 'X-CSRFToken': window.csrf_token },
				data: JSON.stringify(data),
				processData: false,
				dataType: 'json',
				contentType: "application/json",
				type: 'POST',
				success: function(response) {
					console.log("Successfully submitted data");
				},
				error: function(x, y, z) {
					console.log(x, y, z);
				}
			});
		}
	});

	return Slide;

});

