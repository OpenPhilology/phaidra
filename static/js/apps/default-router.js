define(['jquery', 'underscore', 'backbone', 'views/login', 'views/index', 'views/profile/profile'], function($, _, Backbone, LoginView, IndexView, ProfileView) { 

	return Backbone.Router.extend({
		routes: {
			"": "index",
			"login/": "login",
			"profile/": "profile"
		},
		initialize: function() {
			// javascript function for api logout and redirect
			$("#logout-link").click(function(e) {
				e.preventDefault();
				var data = {
					"format" : "json"
				};
				$.ajax({
					url: '/api/v1/user/logout/',
					type: 'GET',
					data: data,
					contentType: 'application/json; charset=utf-8', 
					success: function(response_text) {
						alert("You are logging out.");
						window.location.assign("/home/");	
					},
					error: function(response_text) {
						alert(response_text);
					}
				});
			});
		},
		index: function() {
		},

		// Form handles login page 
		login: function() {
			if (!this.login_view) {
				this.login_view = new LoginView({ el: '#loginform'})
					.render();
			}
		},
		// TODO: Move profile out
		profile: function() {
			if (!this.profile_view) {
				this.profile_view = new ProfileView({ el: '#main'})
					.render();
			}
		}
	});
	
});
