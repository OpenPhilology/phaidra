Phaidra.Views.MultiCompositionSlide = Backbone.View.extend({
	events: {
		"click .options a" : "selectAnswer",
		"click .answers a" : "deselectAnswer"
	},
	initialize: function() {
	},
	render: function() {
		this.$el.html(_.template(this.$el.html(), this.model.attributes));
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
