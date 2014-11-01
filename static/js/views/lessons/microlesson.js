define(['jquery', 
	'underscore', 
	'backbone', 
	'utils', 
	'views/lessons/tasks',
	'text!/templates/js/lessons/microlesson.html'], 
	function($, _, Backbone, Utils, TasksView, Template) { 

		return Backbone.View.extend({
			events: {
				'click .study-notes-nav a': 'toggleNotes'
			},
			template: _.template(Template),
			initialize: function(options) {

				var that = this;
				this.options = options;
				this.user = options.user;

				this.model = this.collection.findWhere({ index: options.index });

				/* Collection has length zero if they navigate directly, 
				 * rather than through Lessons List
				 */ 
				if (this.collection.length === 0 || !this.model) { 
					this.collection.setEndpointLimit(0);
					this.collection.fetch({ success: function() {
						that.fetchTopicDetails(); 
					}});
				}
				else {
					this.fetchTopicDetails();
				}

				// Get our user (needed for showing admin buttons)
				this.user = options.user;
			},
			fetchTopicDetails: function() {
				var match = this.collection.models.filter(function(model) {
					return model.get('id') === this.options.index;
				}.bind(this));

				if (match.length === 0) {
					this.displayError("The lesson you've selected does not exist.");
					return;
				}

				this.model = match[0];
				this.model.on('change', this.render, this);
				this.model.fetch();
			},
			render: function(model) {
				this.model = model;

				// Localize the content
				content = this.model.get('content').filter(function(text) {
					return text.source_lang.short_code === LOCALE;
				});

				if (content.length === 0) {
					this.displayError('This lesson has not been translated into your selected language');
					return this;
				}

				this.$el.html(this.template({
					model: this.model,
					content: content,
					user: this.user
				}));	
				this.$el.find('[data-toggle="tooltip"]').tooltip();
				this.renderTask();

				return this;
			},
			displayError: function(msg) {
				var title = 'An Error Occured';
				msg = msg || 'Apologies for the inconvenience.';

				Utils.displayNotification(title, msg, {
					state: 'error', 
					url: '/lessons', 
					btnName: 'Back to Lessons'
				});		
			},
			renderTask: function() {
				if (!this.tasks) {
					this.tasks_view = new TasksView({ 
						el: this.$el.find('.task'), 
						index: this.options.index,
						topic: this.model
					}); 
				}
				else if (this.tasks_view && this.tasks_view.options.index !== this.options.index) {
					this.tasks_view.initialize({ 
						index: this.options.index,
						topic: this.model
					});
				}
			},
			toggleNotes: function(e) {
				e.preventDefault();
				var target = e.target.dataset.target;

				// First see if they want to de-toggle
				if ($(e.target).hasClass('active')) {
					$(e.target).removeClass('active'); 
					this.$el.find('.study-notes div[data-source="' + target + '"]').hide();
					return;
				}

				// Otherwise, find the correct note to show
				this.$el.find('.study-notes [data-source]').hide();
				this.$el.find('.study-notes-nav li').removeClass('active');
				this.$el.find('.study-notes-nav a[data-target="' + target + '"]').parent().addClass('active');

				if (target === 'alignment') this.renderAlignments();
				else if (target === 'parse-tree') this.renderParseTree();
				else if (target === 'grammar') this.renderGrammar();

			},
			renderAlignments: function(e) {
				var that = this;
				this.$el.find('[data-toggle="morea"]').each(function(i, el) {
					new Morea(el, {
						mode: 'display',
						data: that.constructPhrase(that.phrase),
						targets: el.getAttribute('data-targets').split(','),
						langs: { "grc": { "hr": "Greek", "resource_uri": "", "dir": "ltr" },
							"en": { "hr": "English", "resource_uri": "", "dir": "ltr" } 
						}
					});
				});
				this.$el.find('.vocab-notes div[data-source="alignment"]').show();
			},
			renderParseTree: function(e) {
				var that = this;
				this.$el.find('[data-toggle="daphne"]').each(function(i, el) {
					new Daphne(el, {
						data: that.phrase,
						mode: 'edit',
						width: el.getAttribute('data-width') || 200,
						height: 400,
						initialScale: 0.9
					});
				});
				this.$el.find('.vocab-notes div[data-source="parse-tree"]').show();
			}
		});
	}
);
