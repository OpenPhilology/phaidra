define(['jquery', 
	'underscore', 
	'backbone', 
	'collections/words', 
	'utils', 
	'views/lessons/tasks/sample_task',
	'views/lessons/tasks/type_greek',
	'views/lessons/tasks/identify_letter',
	'views/lessons/tasks/translate_word'], 
	function($, _, Backbone, WordCollection, Utils) { 
		
		return Backbone.View.extend({
			events: {
				'click .corner.right a': 'selectNext',
			},
			initialize: function(options) {

				var that = this;
				this.options = options;
				this.topic = options.topic;

				// New tasks render every time the selected word changes
				this.collection.on('change:selected', this.render, this);

				// Add to word collection based on topic's morph query
				this.collection.fetch({
					success: that.handleSuccess.bind(that),
					error: that.handleError.bind(that)
				});
			},
			render: function() {

				// Must define a task sequence before using this section
				if (!this.topic.get('task_sequence') || this.topic.get('task_sequence').length === 0) {
					var title = 'This lesson has no tasks';
					var msg = 'This lesson does not yet have tasks assigned.';
					var options = { state: 'error', url: '/lessons/', btnName: 'Go back to Lessons' };

					Utils.displayNotification(title, msg, options);
					return;
				}

				// Tasks for this lesson
				var tasks = this.topic.get('task_sequence').tasks.map(function(entry) {
					return entry.task.name;
				});

				// Select our task, then create the view
				var task = tasks[0].split(':')[0];

				// TODO: Make this robust
				var options = { args: tasks[0].split(':')[1] };
				var View = require('views/lessons/tasks/' + task);

				// Remove an existing view if needed
				if (this.task_view) this.task_view.remove();

				this.task_view = new View({ 
					model: this.model, 
					index: this.options.index,
					collection: this.collection,
					DIR: DIR,
					args: options.args,
					topic: this.topic
				}).render();

				// Meaning, we couldn't render this type of task with 
				// the selected word -- try the next one.
				if (!this.task_view) { 
					console.log("Removing task view");
					this.selectNext();
				}
				else { 
					this.task_view.el.setAttribute('style', 'display:none');
					this.$el.append(this.task_view.el);
					this.task_view.$el.fadeIn();
				}
			},
			handleSuccess: function(collection, response, options) {
				console.log(collection, response, options);
				this.selectNext();
			},
			handleError: function(collection, response, options) {
				console.log(collection, response, options);
			},
			selectNext: function(e) { 
				if (e && e.preventDefault) e.preventDefault();

				var next = this.collection.getNextVocab();
				var that = this;

				// Unselect current vocab word
				if (this.model) this.model.set({'selected': false}, {silent: true});

				// Select new vocabulary word
				this.model = next;

				// Grab the container sentence
				var url = this.model.get('sentence_resource_uri');  //+ '?full=True';
				this.collection.url = url;
				this.collection.fetch({
					url: url,
					remove: false,
					merge: true,
					success: function(collection, response, options) {
						that.model.set('selected', true);
					},
					error: function(collection, response, options) {
						console.log("Error", collection, response, options);
					}
				});
			}
		});
	}
);
