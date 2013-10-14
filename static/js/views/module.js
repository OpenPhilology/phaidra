Phaidra.Views.Module = Backbone.View.extend({
	events: {
	},
	initialize: function() {
	},
	render: function() {
		this.$el.find('h3').html(this.model.get('title'));

		// Create as many slides as there are in this module
		var slides = this.model.get('slides').models;
		for (var i = 0; i < slides.length; i++) {
			var selector = '#' + slides[i].get('type');	
			if (selector == '#slide_multi_composition') {
				new Phaidra.Views.MultiCompositionSlide({ model: slides[i], el: this.el }).render().$el.appendTo(this.$el.find('#lesson-content'));;
			}
		}
		
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
