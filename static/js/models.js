define(['jquery', 'underscore', 'backbone', 'text!smyth.json'], function($, _, Backbone, Smyth) {
	var Models = {};
	Smyth = JSON.parse(Smyth);

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

			// Attrs we care about: Smyth ref, task
			this.set('query', Smyth[0][this.attributes.smyth]["query"])
			this.set('type', 'slide_direct_select');

			var taskMapper = {
				'identify_morph_person': function() {
					$.ajax({
						'dataType': 'text',
						//'async': false,
						'url': '/api/word/?format=json&' + that.get('query'),
						'success': function(response) {
							response = JSON.parse(response);
							var len = response.meta.total_count;
							var words = response.objects;
							var answer = words[0];
							
							that.set('content', 'What is the "person" of <span class="greek-text" data-cts="' + answer.CTS + '">' + answer.value + '</span>?');
							that.set('title', 'Morph fun!');
							that.set('options', [
								[{ "value": "1st", "display": "1st" },
								{ "value": "2nd", "display": "2nd" },
								{ "value": "3rd", "display": "3rd" }]
							]);
							that.set('answers', answer.person);
							that.set('require_all', true);
							that.set('require_order', false);
							that.trigger('populated');
						},
						error: function(x, y, z) {
							console.log(x, y, z);
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
