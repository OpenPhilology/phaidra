define(['jquery', 'underscore', 'backbone', 'utils', 'text!/templates/js/grammar-display.html'], function($, _, Backbone, Utils, Template) { 

	var View = Backbone.View.extend({
		events: { 
			'click a': 'selectTopic'
		},
		template: _.template(Template),
		tagName: 'div',
		initialize: function(options) {
			var that = this;
			this.options = options;
		},
		render: function() {
			var that = this;

			this.$el.html(this.template({
				content: Utils.Content, 
				smyth: Utils.Smyth,
				selected: that.options.smyth
			}));

			var urls = Utils.getHTMLbySmyth(that.options.smyth);

			this.$el.find('#grammar-container .row').html('');

			for (var i = 0; i < urls.length; i++) {
				// Append here to preserve the order
				this.$el.find('#grammar-container .row').append('<div data-url="' + urls[i] + '"><div class="corner right"></div></div>');	

				$.ajax({
					url: urls[i],
					dataType: 'text',
					success: function(response) {
						that.$el.find('div[data-url="' + this.url + '"]').append(response);
					},
					error: function(x, y, z) {
						console.log(x, y, z);
					}
				});
			}

			return this;	
		},
		selectTopic: function(e) {
			e.preventDefault();

			Backbone.history.navigate($(e.target).attr('href'), { trigger: true });		
			this.options.smyth = $(e.target).attr('href').split('/')[2];
			this.render();
		}
	});

	return View;
});
