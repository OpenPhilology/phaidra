define(['jquery', 'underscore', 'backbone', 'collections', 'models', 'views/viz-progress-pie', 'text!/templates/js/profile.html'], function($, _, Backbone, Collections, Models, PieView, Template) { 

		/**
		 * Try not to cry when you see this code. It is a disaster, will be fixed!
		 */
		var View = Backbone.View.extend({
			events: {
			},
			template: _.template(Template),
			initialize: function() {
				
				var that = this;

				// Get this user
				new Models.User().fetch({ success: function(model, response, options) {
						that.model = model;

						// TODO: Move this into model
						$.ajax({
							url: '/api/v1/submission/',
							headers: { 'X-CSRFToken': window.csrf_token },
							processData: false,
							dataType: 'json',
							contentType: "application/json",
							type: 'GET',
							success: function(response) {
								that.model.set('submissions', response.objects);
								that.fullRender(that.model);
							},
							error: function(x, y, z) {
								that.$el.find('.pie-container').html('We can\'t retrieve your progress statistics because you\'re not logged in.');
							}
						});

					},
					error: function(model, response, options) {
						console.log(model, response, options);
					}
				});
			},
			render: function() {
				return this;	
			},
			fullRender: function(model) {
				var that = this;
				that.$el.html(that.template({ 
					"model": model,
					"submissions": model.get('submissions')
				}));

				var data =  {
					user: model.get('username'),
					range: "urn:cts:greekLit:tlg0003.tlg001.perseus-grc:1"
				};

				// TODO: Move this into model
				$.ajax({
					url: '/api/v1/visualization/statistics/',
					headers: { 'X-CSRFToken': window.csrf_token },
					data: data,
					dataType: 'json',
					contentType: "application/json",
					type: 'GET',
					success: function(response) {
						new PieView({
							statistics: response.statistics
						}).render();
					},
					error: function(x, y, z) {
						console.log(x, y, z);
					}
				});

			}
	});

	return View;
});
