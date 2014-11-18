define(['jquery', 
	'underscore', 
	'backbone', 
	'views/lessons/tasks/base',
	'utils',
	'typegeek',
	'text!/templates/js/lessons/tasks/identify_letter.html'], 
	function($, _, Backbone, BaseTaskView, Utils, TypeGeek, Template) {

		return BaseTaskView.extend({
			template: _.template(Template),
			events: {
				'submit form': 'checkAnswer'
			},
			initialize: function(options) {
				this.letter = options.args;
				this.topic = options.topic;

				// Answer map
				this.answerMap = {
					"alpha":	{ "upper": "Α", "lower": "α" },
					"beta":		{ "upper": "Β", "lower": "β" },
					"gamma":	{ "upper": "Γ", "lower": "γ" },
					"delta":	{ "upper": "Δ", "lower": "δ" },
					"epsilon":	{ "upper": "Ε", "lower": "ε" },
					"zeta":		{ "upper": "Ζ", "lower": "ζ" },
					"eta":		{ "upper": "Η", "lower": "η" },
					"theta":	{ "upper": "Θ", "lower": "θ" },
					"iota":		{ "upper": "Ι", "lower": "ι" },
					"kappa":	{ "upper": "Κ", "lower": "κ" },
					"lambda":	{ "upper": "Λ", "lower": "λ" },
					"mu":		{ "upper": "Μ", "lower": "μ" },
					"nu":		{ "upper": "Ν", "lower": "ν" },
					"xi":		{ "upper": "Ξ", "lower": "ξ" },
					"omicron":	{ "upper": "Ο", "lower": "ο" },
					"pi":		{ "upper": "Π", "lower": "π" },
					"rho":		{ "upper": "Ρ", "lower": "ρ" },
					"sigma":	{ "upper": "Σ", "lower": "σς" },
					"tau":		{ "upper": "Τ", "lower": "τ" },
					"upsilon":	{ "upper": "Υ", "lower": "υ" },
					"phi":		{ "upper": "Φ", "lower": "φ" },
					"chi":		{ "upper": "Χ", "lower": "χ" },
					"psi":		{ "upper": "Ψ", "lower": "ψ" },
					"omega":	{ "upper": "Ω", "lower": "ω" }
				};

				BaseTaskView.prototype.initialize.apply(this, [options]);
			},

			// Initial render just to make $el available to parent view
			render: function() {
				return this;
			},

			// Called when the sentence is populated
			fullRender: function(options) {

				options = options || {};
				options.state = options.state || 'open';

				this.$el.html(this.template({
					model: this.model,
					options: options,
					letter: this.letter,
					answerMap: this.answerMap
				}));
				
				// Set the starttime for this exercise
				this.starttime = new Date();
				
				var answerBox = this.$el.find('input[type="text"]')[0];
				answerBox.focus();
			},
			checkAnswer: function(e) {
				e.preventDefault();

				// Grab answers from the UI, pass to base_task
				var inputField = $(e.target).find('input');

				// Modify strings before checking accuracy
				var answer = this.letter.toLowerCase().trim();
				var userAnswer = inputField.val().toLowerCase().trim();

				// Check accuracy
				var accuracy = BaseTaskView.prototype.getAccuracy.apply(this, [answer, userAnswer]);

				// Determine new state of the task
				var newState = BaseTaskView.prototype.getNewState.apply(this, [answer, userAnswer]);

				// Send a submission to the server
				this.sendSubmission({ 
					response: userAnswer, 
					accuracy: accuracy,
					ref: this.topic.get('ref'),
					encounteredWords: [""],
					timestamp: (new Date()).toISOString(),
					task: 'identify_letter:' + this.letter,
					starttime: this.starttime.toISOString()
				});

				// Update our UI accordingly
				this.fullRender({ state: newState });
			},
			sendSubmission: function(submission) {
				BaseTaskView.prototype.sendSubmission.apply(this, [submission]);
			}
		});
	}
);
