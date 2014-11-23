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

				// Bindings
				_.bindAll(this, 'selectNext');
				_.bindAll(this, 'handleSuccess');
				_.bindAll(this, 'handleError');

				// New tasks render every time the selected word changes
				this.collection.on('change:selected', this.render, this);

				// Add to word collection based on topic's morph query
				this.collection.fetch({
					success: that.handleSuccess,
					error: that.handleError
				});

				// Make sure our tasks are sorted
				this.topic.sortTasks();

				// Select our task, then create the view
				// Change this.task as we proceed through the sequence
				this.topic.set('attempts', 0);
				this.topic.set('currentTaskIndex', 0);
				this.topic.set('accuracy', 0);

				// Accuracy is adjusted by subviews, and triggers either a re-render
				// with a new word, the user starts over sequence, or proceeds to next
				// lesson.
				this.topic.on('change:accuracy', this.assessTask, this);
			},
			getTaskInfo: function() {

				// Figure out which task we should be working on
				var currentTask = this.topic.getCurrentTask();
				var taskName = currentTask.task.name.split(':')[0];
				var taskArgs = { args: currentTask.task.name.split(':')[1] };

				return { View: require('views/lessons/tasks/' + taskName), args: taskArgs.args };

			},
			render: function() {

				// Must define a task sequence before using this section
				if (!this.topic.get('task_sequence') || this.topic.get('task_sequence').length === 0) {
					var title = gettext('This lesson has no tasks');
					var msg = gettext('This lesson does not yet have tasks assigned.');
					var options = { 
						state: 'error', 
						url: '/lessons/', 
						btnName: gettext('Go back to Lessons')
					};

					Utils.displayNotification(title, msg, options);
					return;
				}

				// Remove an existing view if needed
				if (this.task_view) this.task_view.remove();

				var taskInfo = this.getTaskInfo();

				this.task_view = new taskInfo.View({ 
					model: this.model, 
					index: this.options.index,
					collection: this.collection,
					DIR: DIR,
					args: taskInfo.args,
					topic: this.topic
				}).render();

				// Meaning, we couldn't render this type of task with 
				// the selected word -- try the next one.
				if (!this.task_view) { 
					this.selectNext();
				}
				else { 
					this.task_view.el.setAttribute('style', 'display:none');
					this.$el.append(this.task_view.el);
					this.task_view.$el.fadeIn();
				}
			},
			handleSuccess: function(collection, response, options) {
				this.selectNext();
			},
			handleError: function(collection, response, options) {
				var title = gettext('Trouble loading textual data.');
				var msg = gettext('We could not word the vocabulary related to this unit.');
				var options = {
					state: 'error',
					url: '/lessons/',
					btnName: gettext('Go back to Lessons')
				};

				Utils.displayNotification(title, msg, options);
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
			},
			assessTask: function(model) {
				var attempts = model.get('attempts');
				var accuracy = model.get('accuracy');
				var min_attempts = model.get('task_sequence').min_attempts;
				var max_attempts = model.get('task_sequence').max_attempts;
				var target_accuracy = model.get('task_sequence').target_accuracy;
				var current_task = model.getCurrentTask();
				
				console.log("attempts", attempts, "accuracy", accuracy, "min attempts", min_attempts, "max attempts", max_attempts, "target accuracy", target_accuracy);

				// Get the task we're working on -- see if they got it right.
				// If not, do nothing. 
				if (current_task.state !== 'success') return;

				// If yes, either advanceTask, lowerBar, or triggerCompletion.
				if (accuracy <= target_accuracy || attempts <= min_attempts)
					this._advanceTask(model);
				else if (attempts >= max_attempts || max_attempts === 0)
					this._advanceTask(model);
				else if (attempts === max_attempts && accuracy < target_accuracy)
					this._lowerBar(model);
				else
					this._triggerCompletion(model);
			},
			_lowerBar: function(topic) {
				// Reset task seq params so that user passes as soon as they reach proficiency
				console.log("lower bar");

				topic.set('attempts', 0);
				topic.set('accuracy', 0);
				topic.set('min_attempts', 1);
				topic.set('max_attempts', 0);

				this._advanceTask(topic);
			},
			_advanceTask: function(topic) {
				// Move to the next slide in the sequence
				console.log("advance task");
				var index = topic.get('currentTaskIndex');

				// Set the next task
				if (index < topic.get('task_sequence').tasks.length - 1)
					topic.set('currentTaskIndex', (index + 1));
				else
					topic.set('currentTaskIndex', 0);

				setTimeout(this.selectNext, 3 * 1000);
			},
			_triggerCompletion: function(topic) {
				// Congratulations! Forward to next unit.
				var title = gettext('Great Job!');
				var msg = gettext('You completed this unit!');
				var options = { 
					state: 'error', 
					url: '/lessons/', 
					btnName: gettext('Go back to Lessons')
				};

				Utils.displayNotification(title, msg, options);
			}
		});
	}
);
