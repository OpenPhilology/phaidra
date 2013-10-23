Phaidra.Views.MultiCompositionSlide = Backbone.View.extend({
	tagName: 'div',
	className: 'slide-unit',
	events: {
		"click .options a" : "selectAnswer",
		"click .answers a" : "deselectAnswer"
	},
	initialize: function(options) {
		this.$el.html(options.template(this.model.attributes));
	},
	render: function() {
		return this;	
	},
	selectAnswer: function(e) {
		e.preventDefault();

		var selectedOption = $(e.target).parent();
		var answer = selectedOption.clone();

		answer.data('source', selectedOption);

		this.$el.find('ul.answers').append(answer);
		selectedOption.hide();
	},
	deselectAnswer: function(e) {
		e.preventDefault();

		var answer = $(e.target).parent();
		answer.hide();

		answer.data('source').show();

	}
});
