define(['jquery', 
	'underscore', 
	'backbone', 
	'collections/words', 
	'utils', 
	'views/lessons/tasks/translate_word', 
	'views/lessons/tasks/build_tree', 
	'views/lessons/tasks/identify_morph', 
	'views/lessons/tasks/provide_article', 
	'views/lessons/tasks/align_phrase'], 
	function($, _, Backbone, WordCollection, Utils) { 
		
		return Backbone.View.extend({
			events: {
				'click .corner.right a': 'selectNext',
			},
			initialize: function(options) {

				var that = this;
				this.options = options;
				this.topic = options.topic;

				// Instantiate our collection, tell it how to populate vocabulary
				this.collection = new WordCollection([], {
					url: '/api/v1/word/?' + that.topic.get('query')
				});

				// New tasks render every time the selected word changes
				this.collection.on('change:selected', this.render, this);

				// Add to word collection based on topic's morph query
				this.collection.fetch({
					success: that.handleSuccess.bind(that),
					error: that.handleError.bind(that)
				});
			},
			render: function() {
				// TODO: get this in a smart way, not random
				var tasks = ['translate_word', 
					'align_phrase', 
					'build_tree', 
					'identify_morph', 
					'provide_article'];

				var i = Math.floor(Math.random() * (tasks.length - 1));
				var View = require('views/lessons/tasks/' + tasks[0]);

				// Remove an existing view if needed
				if (this.task_view) this.task_view.remove();

				this.task_view = new View({ 
					model: this.model, 
					index: this.options.index,
					collection: this.collection,
					DIR: DIR
				}).render();

				// Meaning, we couldn't render this type of task with 
				// the selected word -- try the next one.
				if (!this.task_view) { 
					console.log("Removing task view");
					this.selectNext();
				}
				else 
					this.$el.append(this.task_view.el);
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

				console.log("selectNext called");
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
						console.log(that.collection.indexOf(that.model));
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
