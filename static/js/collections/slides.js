define(['jquery', 'underscore', 'backbone', 'models/slide', 'utils'], function($, _, Backbone, SlideModel, Utils) {

	return Backbone.Collection.extend({
		model: SlideModel,
		initialize: function(models, options) {
			_.bindAll(this, 'insertVocab');
			_.bindAll(this, 'insertSlides');

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

			// Set attributes on this section
			this.meta('initLength', 0);
			this.meta('moduleTitle', module.title);
			this.meta('sectionTitle', section.title);
			this.meta('slides', section.slides);

			// Pull vocabulary for this section
			this.meta('vocab', new Collections.Words([], { grammar: _.compact(_.pluck(this.meta('slides'), 'smyth')) }));
			this.meta('vocab').on('populated', this.insertVocab, this);
			this.insertSlides(this.meta('slides'));

			// Initiate collection of vocabulary words
			this.meta('vocab').populateVocab();

		},
		insertSlides: function(slides) {

			// Create skeleton vocab slide
			var vocSlide = { type: 'slide_vocab' };
			slides.splice(1, 0, vocSlide);

			for (var i = 0, slide; slide = slides[i]; i++) {
				slide.title = this.meta('sectionTitle');
				this.add(slide);
				this.meta('initLength', (1 + this.meta('initLength')));
				this.insertExercises(slide, slide.smyth);
			}
		},
		insertVocab: function(options) {
			console.log("insert vocab called");

			var slide = this.findWhere({ type: 'slide_vocab' });
			slide.set('vocab', this.meta('vocab'));
			slide.set('populated', true);

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

});
