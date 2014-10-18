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

				console.log(this.collection);

				/* Instantiate our collection, tell it how to populate vocabulary
				this.collection = new WordCollection([], { grammar: options.ref });
				this.collection.on('populated', this.selectNext, this);
				this.collection.on('change:selected', this.render, this);
				this.collection.populateVocab();*/ 
			},
			render: function() {
				var tasks = Utils.getLesson(this.options.ref); 

				// TODO: get this in a smart way, not random
				var tasks = ['translate_word', 'align_phrase', 'build_tree', 'identify_morph', 'provide_article'];
				var i = Math.floor(Math.random() * (tasks.length - 1));
				var View = require('views/lessons/tasks/' + tasks[0]);

				// Remove an existing view if needed
				if (this.task_view) this.task_view.remove();

				this.task_view = new View({ model: this.model, el: '.subtask' , index: this.options.index }).render();

				// Meaning, we couldn't render this type of task with the selected word
				if (!this.task_view) this.selectNext();
			},
			selectNext: function(e) { 
				if (e) e.preventDefault();

				var next = this.collection.getNextRandom(this.options.ref, this.model);
				if (this.model) this.model.set({'selected': false}, {silent: true});
				this.model = next;

				var that = this;
				this.model.fetchSentence(this.model.get('CTS'), {
					success: function() {
						that.model.set('selected', true);
					}
				});
			}
		});
	}
);
