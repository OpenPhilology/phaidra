define(['jquery', 'underscore', 'backbone', 'models', 'collections', 'views/login', 'views/index', 'views/home'], 
		function($, _, Backbone, Models, Collections, LoginView, IndexView, HomeView) { 

	var Router = {};
	Router.Router = Backbone.Router.extend({
		routes: {
			"": "index",

			// Form handles login page
			"login/": "showLogin",

			// Traditional Grammar Routes
			"grammar/:smyth": "showGrammar",
		},
		initialize: function() {
			// Create/Populate necessary models and collections

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
			/*if (!this.index_view) {
				this.index_view = new IndexView({ el: '.container' }).render();
			}*/
		},

		// Form handles login page 
		showLogin: function() {
			if (!this.login_view) {
				this.login_view = new LoginView({ el: '#loginform'})
					.render();
			}
		},

		// Traditional Grammar View
		showGrammar: function(smyth) {
			if (!this.grammar_view) {
				this.grammar_view = new GrammarView({ el: '#main', smyth: smyth})
					.render()
					.$el
					.appendTo($('#main'));
			}
		}
	});
	
	return Router;
});
