define(['jquery', 'underscore', 'backbone', 'utils'], function($, _, Backbone, Utils) { 

		var View = Backbone.View.extend({
			events: {
				'submit form': 'signup',
				'click #start-link': 'showForm'
			},
			initialize: function() {
				// If user is already logged in, redirect
			},
			render: function() {
				var container = this.$el.find('.module-container .row');
				for (var i = 0; i < Utils.Content.length; i++) {
					var unit = Utils.Content[i];
					console.log(unit);

					var div = $('<div>', {
						class: 'col-md-3 col-sm-4',
						style: 'display: none',
						html: function() {
							var str = '<a href="/module/' + i + '/section/0/slide/0" class="module ' + (unit.category || 'noun') + '">';

							if (unit.thumbnail) {
								str += '<img src="/static/images/' + (unit.thumbnail || 'blah.png') + '">';
							}

							str += '<div>';
							str += '<h3>' + unit.title + '</h3>';
							
							for (var j = 0; j < unit.modules.length; j++) {
								str += '<span class="circle" title="' + unit.modules[j].title + '"></span>';
							}
							str += '</div></a>';
							return str;
						}
					});
					div.appendTo(container);
				}

				var elements = this.$el.find('.module-container .row .col-md-3'); 
				$.each(elements, function(i, el) {
					setTimeout(function() {
						$(el).fadeIn();
					}, (i * 0.75) * 50);
				});

				return this;	
			},
		});

	return View;
});
