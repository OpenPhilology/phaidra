define(['jquery', 'underscore', 'backbone', 'models', 'utils'], function($, _, Backbone, Models, Utils) {

	var Collections = {};

	// Some modifications to Backbone to work with Tastypie
	Collections.Base = Backbone.Collection.extend({
		urlRoot: '/api/',
		url: function() {
			return this.urlRoot + '/' + this.model.prototype.defaults.modelName + '/';		
		},
		parse: function(response) {
			// Since Tastypie gives us metadata about our objects, store that on the collection
			// and assign the actual objects to the collection itself.

			if (response && response.meta)
				this.meta = response.meta;

			return (response && response.objects ? response.objects : response) || response;
		},
		sync: function(options) {
			// Make sure that CSRF Tokens are sent with every request
			// GetCookie function from: https://docs.djangoproject.com/en/dev/ref/contrib/csrf/

			var getcookie = function(name) {
				var value = null;
				if (document.cookie && document.cookie != '') {
					var cookies = document.cookie.split(';');
					for (var i = 0; i < cookies.length; i++) {
						var cookie = $.trim(cookies[i]);
						if (cookie.substring(0, name.length + 1) == (name + '=')) {
							value = decodeURIComponent(cookie.substring(name.length + 1));
							break;
						}
					}
				}
				return value;
			}

			options.headers = {
				'X-CSRFToken': getcookie('csrftoken')
			};

			(_.bind(Backbone.Collection.prototype.sync, this, options))();
		}
	});

	Collections.Slides = Backbone.Collection.extend({
		model: Models.Slide,
		initialize: function(models, options) {
			var that = this;

			// Keep track of metadata about the collection
			if (!this._meta)
				this._meta = [];

			this.meta = function(prop, value) {
				if (value == undefined)
					return this._meta[prop];
				else
					this._meta[prop] = value;
			};

			that.meta('module', parseInt(options.module));
			that.meta('section', parseInt(options.section));
		},
		populate: function(collection) {
			var that = this;
			var module = Utils.Content[this.meta('module')];
			var section = module.modules[this.meta('section')];
			var slides = section.slides;

			// Set attributes on this section
			this.meta('initLength', slides.length);
			this.meta('moduleTitle', module.title);
			this.meta('sectionTitle', section.title);

			for (var i = 0, slide; slide = slides[i]; i++) {
				slide.title = this.meta('sectionTitle');
				this.add(slide);
				this.insertExercises(slide, slide.smyth);
			}
		},
		insertExercises: function(slide, smyth, index) {
			if (!slide.smyth)
				return;

			var newSlides = [];
			if (slide.tasks) {
				var tasks = this.insertTasks(slide.tasks, slide.smyth);
				newSlides = newSlides.concat(tasks);
			}

			var questions = this.insertQuestions(slide.smyth);
			newSlides = newSlides.concat(questions);
			newSlides = _.shuffle(newSlides);

			if (newSlides.length === 0)
				return;
			else if (index) 
				this.add(newSlides, { at: index });
			else 
				this.add(newSlides);
		},
		insertTasks: function(tasks, smyth) {
			var matches = Utils.Tasks.filter(function(t) {
				t.smyth = smyth;
				return tasks.indexOf(t.task) !== -1;
			});

			// Create at least five tasks
			while (matches.length < 5) {
				matches = matches.concat(matches);
			}
			return _.shuffle(matches).splice(0, 5);
		},
		insertQuestions: function(smyth) {
			// Here we find out what questions are available for this subject
			var questions = Utils.Questions.filter(function(q) {
				return q.smyth === smyth;
			});
			return questions;
		}
	});

	Collections.Documents = Backbone.Collection.extend({
		model: Models.Document,
		url: '/api/v1/document/',
		parse: function(response) {

			// Flatten our references to sentence URIs
			for (var i = 0; i < response.objects.length; i++) {
				response.objects[i].sentences = response.objects[i].sentences.map(function(el) {
					return el.resource_uri;
				});
			}
			this.add(response.objects);
		}
	});

	Collections.Words = Backbone.Collection.extend({
		model: Models.Word
	});

	return Collections;
});
