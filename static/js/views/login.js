define(['jquery', 'underscore', 'backbone'], function($, _, Backbone) { 

		var View = Backbone.View.extend({
			events: {
				'submit #login-form': 'login'
			},
			initialize: function() {
				// If user is already logged in, redirect
			},
			render: function() {
				return this;	
			},
			login: function(e) {
				e.preventDefault();

				var form = this.$el.find('#login-form');
				var data = {
					"username" : form.find('input[name="username"]').val(),
					"password" : form.find('input[name="password"]').val()
				};

				$.ajax({
					url: '/api/v1/user/login/',
					type: 'POST',
					contentType: 'application/json; charset=utf-8', 
					dataType: 'json',
					data: JSON.stringify(data),
					success: function(response_text) {
						var dest = '/home/';
						if (window.location.search) {
							dest = window.location.search.split("=")[1];
						}

						window.location.assign(dest);	
					},
					error: function(response_text) {
						alert("Try again");
					}
				});
			}
		});

	return View;
});
