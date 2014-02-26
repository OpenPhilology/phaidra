define(['jquery', 'underscore', 'backbone'], function($, _, Backbone) {
	var Models = {};

	Models.User = Backbone.Model.extend({
		defaults: {
			'modelName': 'user',
		},
		url: '/api/user/',
		parse: function(response) {
			if (response && response.meta)
				this.meta = response.meta;

			return response && response.objects && (_.isArray(response.objects) ? response.objects[0] : response.objects) 
				|| response;
		}
	});

	Models.Lesson = Backbone.Model.extend({
		defaults: {
			'modelName': 'lesson'
		}
	});

	Models.Slide = Backbone.Model.extend({
		initialize: function() {
			_.bindAll(this, 'checkAnswer');
		},
		constructor: function(attributes, options) {

			//Backbone.Model.apply(this, arguments);
			Backbone.Model.prototype.constructor.call(this, attributes);

			// Slide is dynamic if it has a task defined
			// Or it has all set attributes already (as is case for hand-written slides) 

			if (attributes.task)
				this.fillAttributes(attributes, options)
		},
		defaults: {
			'modelName': 'slide',
		},
		fillAttributes: function(attributes, options) {
			
			var that = this;

			var taskMapper = {
				/*
					If the task is "identify_morph_noun", we expect the inputs:
					* lemmas
					* filter
				*/
				'identify_morph_noun': function() {

					var index = Math.floor((Math.random() * attributes.inputs.lemmas.length));
					var lemma = attributes.inputs.lemmas[index];

					$.ajax({
						url: '/api/sentence/get_one_random/?format=json&lemma=' + lemma + '&' + attributes.inputs.filter,
						async: false,
						dataType: 'json',
						success: function(response_text) {
							that.set({
								title: "Exercise: Identify the Case!",
								responseText: response_text,
								lemma: lemma,
								content: response_text.sentence,
								options: [
									[
										{
											"value": "Nominative",
											"display": "Nominative"
										},
										{
											"value": "Genitive",
											"display": "Genitive"
										},
										{
											"value": "Dative",
											"display": "Dative"
										}
									]
								],
								answers: ["Dative"],
								successMsg: "Right",
								hintMsg: "Wrong",
								failureMsg: "Correct was",
								require_order: true,
								require_all: true
							});
						},
						error: function(xhr, status, error) {
							console.log(xhr, status, error);
						}
					});
				}
			};

			taskMapper[attributes.task]();

		},
		checkAnswer: function(attempt) {
			if (typeof(attempt) == 'string')
				attempt = [attempt]

			// Check if all submitted attempts are somewhere in answers
			if (!Boolean(this.get('require_all'))) {
				for (var i = 0; i < attempt.length; i++)
					if (this.get('answers').indexOf(attempt[i]) == -1)
						return false;

				return true;
			}
			// Require order implies that require_all is also true
			else if (Boolean(this.get('require_order'))) {
				if (this.get('answers').length !== attempt.length)
					return false;
				else {
					for (var i = 0; i < attempt.length; i++) {
						if (attempt[i] != this.get('answers')[i]) 
							return false;
					}

					return true;
				}
			}
			// All Required, but order is not required
			else if (Boolean(this.get('require_all')) && !Boolean(this.get('require_order')))
				return $(attempt).not(this.get('answers')).length == 0 && $(this.get('answers')).not(attempt).length == 0;
			else
				return false;
		}
	});

	Models.Word = Backbone.Model.extend({
		defaults: {
			'modelName': 'word',
			/*
			'def': 'Definition',
			'seen': 0,
			'lesson': '3'
			*/
		}
	});

	//_.extend(Models.Lesson.defaults, Models.Base.defaults);
	//_.extend(Models.Module.defaults, Models.Base.defaults);
	//_.extend(Models.Slide.defaults, Models.Base.defaults);
	//_.extend(Models.Word.defaults, Models.Base.defaults);

	return Models;
});
