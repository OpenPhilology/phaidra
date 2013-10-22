Phaidra.Views.InfoSlide = Backbone.View.extend({
	initialize: function() {

		var that = this;

		/*
		View takes either a Slide model or a path to a simple HTML page 
		*/
		if (this.model.get('includeHTML')) {
			$.ajax({
				url: that.model.get('includeHTML'),
				type: 'GET',
				async: false,
				success: function(responseText) {
					that.template = _.template(responseText);
					that.el = that.template(that.model.attributes);
					that.$el = $(that.el);
				},
				error: function(responseText) {
					console.log("Problem!");	
				}
			});
		}
		else {
			this.template = _.template(this.$el.find('#slide_info').html());
			this.el = this.template(this.model.attributes);
			this.$el = $(this.el);
		}

	},
	render: function() {
		// Append a 'next' button
		
		//var index = Phaidra.modules.indexOf(this.model);
		//this.$el.append('<p><a href="' + index + '">Continue</a></p>');

		return this;
	}
});
