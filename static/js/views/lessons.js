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
				container.html('');
				
				console.log(Utils.Smyth);
				console.log(Utils.Microlessons);
				console.log(Utils.getLesson('s9'));

				// TODO: Move this into template
				Utils.Microlessons.forEach(function(lesson) {
					var data = Utils.getLesson(lesson);
					var smyth = Utils.getSmyth(lesson);

					// Means we have a smyth query but no learning content for it yet
					if (!data) return;

					var div = $('<div>', {
						class: 'col-md-3 col-sm-4',
						style: 'display: none',
						html: function() {
							var str = '<a href="/lessons/' + lesson + '" class="module ' + data.category +'">';
							str += data.thumbnail ? '<img src="' + data.thumbnail + '">' : '';
							str += '<div>';
							str += '<h3>' + smyth.title + '</h3>';
							str += '</div></a>';
							return str;
						}
					});
					div.appendTo(container);
				});

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
