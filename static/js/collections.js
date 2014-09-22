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
			_.bindAll(this, 'insertVocab');

			// Keep track of metadata about the collection
			if (!this._meta)
				this._meta = [];

			this.meta = function(prop, value) {
				if (value == undefined)
					return this._meta[prop];
				else
					this._meta[prop] = value;
			};

			this.meta('module', parseInt(options.module));
			this.meta('section', parseInt(options.section));
		},
		populate: function(collection) {
			var that = this;
			var module = Utils.Content[this.meta('module')];
			var section = module.modules[this.meta('section')];
			var slides = section.slides;

			// Set attributes on this section
			this.meta('initLength', 0);
			this.meta('moduleTitle', module.title);
			this.meta('sectionTitle', section.title);

			// Pull vocabulary for this section
			this.meta('vocab', new Collections.Words([], { grammar: _.compact(_.pluck(slides, 'smyth')) }));
			this.meta('vocab').on('populated', this.insertVocab, this);

			// Add slides and exercises
			for (var i = 0, slide; slide = slides[i]; i++) {
				slide.title = this.meta('sectionTitle');
				this.add(slide);
				this.meta('initLength', (1 + this.meta('initLength')));
				console.log("length, after slide add", this.meta('initLength'));
				this.insertExercises(slide, slide.smyth);
				console.log("length, after exercise add", this.meta('initLength'));
			}

			// Initiate collection of vocabulary words
			this.meta('vocab').populateVocab();

		},
		insertVocab: function(options) {
			console.log(this.meta('vocab'));

			//this.add({ type: 'slide_vocab', vocab: this.meta('vocab'), populated: true }).at(1);
			//this.meta('initLength', this.meta('initLength') + 1);

			if (options && options.success)
				options.success();
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

			// This slide has no associated tasks or grammar questions
			if (newSlides.length === 0) return;

			// Give all the slides an index -- needed for inserting slides later
			var idx = this.meta('initLength');
			newSlides = JSON.parse(JSON.stringify(newSlides));
			this.meta('initLength', idx + newSlides.length);
			this.add(newSlides);
		},
		insertTasks: function(tasks, smyth) {
			var matches = Utils.Tasks.filter(function(t) {
				t.smyth = smyth;
				return tasks.indexOf(t.task) !== -1;
			});

			return matches;
		},
		insertQuestions: function(smyth) {
			// Here we find out what questions are available for this subject
			var questions = Utils.Questions.filter(function(q) {
				return q.smyth === smyth;
			});
			return questions;
		},
		makeStats: function() {
			var stats = {
				"avgSpeed": "1s",
				"quickestQuestion": "5ms",
				"skillCount": "5"
			};

			// Get slides which were questions
			var answered = _.reject(this.models, function(m) {
				return typeof(m.get('accuracy')) === 'undefined';
			});

			// Accuracy array
			var vals = answered.map(function(a) {
				return a.get('accuracy');
			});
			stats.accuracy = (_.reduce(vals, function(memo, num) {
				return memo + num;
			}, 0) / vals.length).toFixed(2);

			// Time difference array
			var times = answered.map(function(a) {
				return (a.get('endtime') - a.get('starttime')) / 1000;
			});
			stats.quickestQuestion = 100000000000;
			stats.avgSpeed = (_.reduce(times, function(memo, num) {
				stats.quickestQuestion = num < stats.quickestQuestion ? num : stats.quickestQuestion;
				return memo + num;
			}, 0) / times.length).toFixed(2);
			stats.quickestQuestion = stats.quickestQuestion.toFixed(2);

			// Skill array -- ignore our added in # signs
			var skills = answered.map(function(m) {
				var s = m.get('smyth');
				if (s) {
					var end = m.get('smyth').indexOf('#') || m.get('smyth').length;
					return m.get('smyth').substring(0, end);
				};
			});
			stats.skillCount = skills.length;

			return stats;
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
			var docs = this.calcCompletion(response.objects);
			this.add(docs);
		},
		calcCompletion: function(docs) {
			docs.forEach(function(m) {
				// Use CTS to group
				var work = m.CTS.split(':')[3].split('.');
				var common = work[0] + work[1];
				m.family = common;
			});
			docs.forEach(function(m) {
				var orig = docs.filter(function(model) {
					return model.common === m.common && model.lang === 'grc';
				})[0];

				m.completion = (m.sentences.length / orig.sentences.length) * 100;

			}.bind(this));
			
			return docs;
		}
	});

	Collections.UserDocuments = Backbone.Collection.extend ({ 
		model: Models.UserDocument,
		url: '/api/v1/user_document/',
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
		model: Models.Word,
		initialize: function(models, options) {
			// Keep track of metadata about the collection
			if (!this._meta)
				this._meta = [];

			this.meta = function(prop, value) {
				if (value == undefined)
					return this._meta[prop];
				else
					this._meta[prop] = value;
			};

			if (options && options.grammar) 
				this.meta('grammar', options.grammar);
		},
		populateVocab: function(collection) {

			var that = this;
			var calls = [];

			this.meta('grammar').forEach(function(val, i, arr) {
				calls.push($.ajax('/api/v1/word/', {
					data: { "smyth": val, "limit": 0 },
					success: function(response) {
						that.add(response.objects);			
					},
					error: function(x, y, z) {
						console.log(x, y, z);
					}
				}));
			});

			$.when.apply(this, calls).done(function() {
				that.meta('populated', true);
				that.trigger('populated');
			});
		},
		filterVocabulary: function() {
			var groupedByFreq = _.reduce(this.models, function(map, model) {
				var lemma = model.attributes.lemma;
				(map[lemma] || (map[lemma] = [])).push(model);
				return map;
			}, {});
			
			var candidates = [];

			// Try to get good definitions based on what alignment data is likely to be like
			switch(this.models[0].get('pos')) {
				case 'noun':
					candidates = this.where({ 'case': 'gen', 'number': 'sg' });
					break;
				case 'verb':
					candidates = this.where({ 'pos': 'verb' });
					break;
				default:
					candidates = this.where({ 'lang': 'grc' });
					break;
			}

			candidates = _.uniq(_.map(candidates, function(c) { return c.get('lemma'); }));
			return candidates;
		}
	});

	return Collections;
});
