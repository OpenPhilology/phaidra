define(['jquery', 'underscore', 'backbone'], function($, _, Backbone) { 

		var View = Backbone.View.extend({
			events: {
				'submit form': 'signup',
				'click #start-link': 'showForm'
			},
			initialize: function() {
				console.log("initializing index");
				// If user is already logged in, redirect
			},
			render: function() {
				return this;	
			},
			showForm: function(e) {
				e.preventDefault();
				var that = this;

				this.$el.find('#greeting-text').slideUp('slow', function() {
					that.$el.find('#register-text').slideDown('slow');
				});
			},
			signup: function(e) {
				e.preventDefault();

				var data = this.$el.find('form').serialize();

				$.ajax({
					url: '/api/v1/create_user/',
					type: 'POST',
					contentType: 'application/json; charset=utf-8', 
					dataType: 'json',
					data: data,
					success: function(response_text) {
						window.location.assign("/home/");	
					},
					error: function(response_text) {
						alert("Try again");
					}
				});
			}
		});

	return View;
});
