define(['jquery', 'underscore', 'backbone', 'views/login', 'views/index', 'views/profile/profile'], function($, _, Backbone, LoginView, IndexView, ProfileView) { 

	return Backbone.Router.extend({
		routes: {
			"": "index",
			"login/": "login",
			"profile/": "profile"
		},
		initialize: function() {
			this.route(/^(.*?)\/login\/(.*?)$/, 'login');
			this.route(/^(.*?)\/profile\/(.*?)$/, 'profile');
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
