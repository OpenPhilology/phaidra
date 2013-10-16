Phaidra.Views.InfoSlide = Backbone.View.extend({
	initialize: function() {
		this.template = _.template(this.$el.find('#slide_info').html());
		this.el = this.template(this.model.attributes);
		this.$el = $(this.el);
	},
	render: function() {
		return this;
	}
});
