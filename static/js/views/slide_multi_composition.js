Phaidra.Views.MultiCompositionSlide = Backbone.View.extend({
	events: {
		"click .options a" : "selectAnswer",
		"click .answers a" : "deselectAnswer"
	},
	initialize: function() {
		this.template = _.template(this.$el.find('#slide_multi_composition').html());
		this.el = this.template(this.model.attributes);
		this.$el = $(this.el);
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
