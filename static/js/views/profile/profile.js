define(['jquery', 
	'underscore', 
	'backbone', 
	'models/user', 
	'views/vis/progress-donuts', 
	'views/vis/thuc-knowledge',
	'text!/templates/profile.html'], 
	function($, _, Backbone, UserModel, PieView, ThucKnowledgeView, Template) { 

		/**
		 * Try not to cry when you see this code. It is a disaster, will be fixed!
		 */
		return Backbone.View.extend({
			events: { },
			template: _.template(Template),
			initialize: function() {
				
				var that = this;

				// Get this user
				new UserModel().fetch({ success: function(model, response, options) {
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

				var data =  {
					user: model.get('username'),
					range: "urn:cts:greekLit:tlg0003.tlg001.perseus-grc"
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
				
				new ThucKnowledgeView({
					el: this.$el.find('#thuc-knowledge')
				}).render();
			}
		}
	);
});
