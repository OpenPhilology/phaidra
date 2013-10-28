define(['jquery', 'underscore', 'backbone'], function($, _, Backbone) {
	var Models = {};

	Models.Base = Backbone.Model.extend({
		defaults: {
			'modelName': 'base',
			'urlRoot': '/api/'
		},
		url: function() {
			return this.urlRoot + this.modelName;		
		},
	});

	Models.Lesson = Models.Base.extend({
		defaults: {
			'modelMame': 'lesson'
		}
	});

	Models.Module = Models.Base.extend({
		defaults: {
			'modelName': 'module',
			'levels': 0
		}
	});

	Models.Slide = Models.Base.extend({
		defaults: {
			'modelName': 'slide',
			/*'uid': 0,
			'title': '',
			'moduleTitle': '',
			'type': '',		// Determines the view and template that will be used
			'content': '',
			'options': [],
			'submission': ''*/
		},
		// Check user's submission against the server 
		checkSubmission: function(submission, options) {
			var that = this;

			this.save({ 
					submission: submission 
				},
				{ 
					patch: true,

					// Allow views to handle how passing and failing submissions are handled
					success: function(model, response, options) {
						if (that.options && that.options.success)
							that.options.success(model, response, options);					
					},
					error: function(model, xhr, options) {
						if (that.options && that.options.error)
							that.options.error(model, xhr, options);
					}
				}
			);
		}
	});

	Models.Word = Models.Base.extend({
		defaults: {
			'modelName': 'word',
			/*
			'def': 'Definition',
			'seen': 0,
			'lesson': '3'
			*/
		}
	});

	_.extend(Models.Lesson.defaults, Models.Base.defaults);
	_.extend(Models.Module.defaults, Models.Base.defaults);
	_.extend(Models.Slide.defaults, Models.Base.defaults);
	_.extend(Models.Word.defaults, Models.Base.defaults);

	return Models;
});
