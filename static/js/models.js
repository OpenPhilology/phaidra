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

	Models.Module = Backbone.Model.extend({
		defaults: {
			'modelName': 'module',
			'levels': 0
		}
	});

	Models.Slide = Backbone.Model.extend({
		initialize: function() {
			_.bindAll(this, 'checkAnswer');
		},
		defaults: {
			'modelName': 'slide',
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
