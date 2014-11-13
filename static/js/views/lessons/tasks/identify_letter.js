define(['jquery', 
	'underscore', 
	'backbone', 
	'views/lessons/tasks/base_task',
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
				
				var answerBox = this.$el.find('input[type="text"]')[0];
				answerBox.focus();
			},
			checkAnswer: function(e) {
				e.preventDefault();

				// Grab answers from the UI, pass to base_task
				var inputField = $(e.target).find('input');
				var answer = this.letter.toLowerCase().trim();
				var userAnswer = inputField.val().toLowerCase().trim();

				// Call our BaseTask's answer checking functionality 
				var newState = BaseTaskView.prototype.checkAnswer.apply(this, [answer, userAnswer]);

				// Update our UI accordingly
				this.fullRender({ state: newState });
			}
		});
	}
);
