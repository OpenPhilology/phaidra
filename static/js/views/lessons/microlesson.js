define(['jquery', 'underscore', 'backbone', 'collections/words', 'utils', 'text!/templates/js/lessons/microlesson.html', 
	'views/lessons/tasks/translate_word', 'views/lessons/tasks/build_tree', 'views/lessons/tasks/identify_morph', 'views/lessons/tasks/provide_article', 'views/lessons/tasks/align_phrase'], 
	function($, _, Backbone, WordCollection, Utils, Template) { 

	var View = Backbone.View.extend({
		events: {
			'click .corner.right a': 'skipQuestion',
			'click #topic-panel .panel-title a': 'viewGrammarTopic',
			'click .study-notes-nav a': 'toggleNotes'
		},
		template: _.template(Template),
		initialize: function(options) {

			var that = this;
			this.options = options;

			// Instantiate our collection, tell it how to populate vocabulary
			this.collection = new WordCollection([], { grammar: options.ref });
			this.collection.on('populated', this.selectNext, this);
			this.collection.on('change:selected', this.render, this);
			this.collection.populateVocab();
		},
		selectNext: function() {
			var oldModel = this.collection.findWhere({ selected: true });
			if (oldModel) oldModel.set('selected', false);
			this.model = this.collection.at(1);

			var that = this;
			this.model.fetchSentence(this.model.get('CTS'), {
				success: function() {
					that.model.set('selected', true);
				}
			});
		},
		render: function(model) {
			this.model = model;

			this.$el.html(this.template({
				model: this.model,
				toc: this.getTableOfContents(),
			}));	
			this.$el.find('[data-toggle="tooltip"]').tooltip();
			this.renderTask();

			return this;
		},
		renderTask: function() {
			var tasks = Utils.getLesson(this.options.ref); 

			// TODO: get this in a smart way, not random
			var tasks = ['translate_word', 'align_phrase', 'build_tree', 'identify_morph', 'provide_article'];
			var i = Math.floor(Math.random() * (tasks.length - 1));
			var View = require('views/lessons/tasks/' + tasks[0]);
			this.task_view = new View({ model: this.model, el: '.subtask' }).render();
		},
		getTableOfContents: function() {
			var topics = Utils.getHTMLbySmyth(this.model.getGrammar() || this.options.ref);
			return topics.map(function(topic) {
				var title = Utils.Smyth.filter(function(s) { return s.ref === topic.smyth })[0].title;
				topic.title = title;
				return topic;
			});
		},
		selectModel: function() {

		},
		skipQuestion: function() {

		},
		viewGrammarTopic: function(e) {
			var topic = e.target.dataset.topic;
			var el = this.$el.find('.panel-body[data-topic="' + topic + '"]');

			if (el.children().length !== 0)
				return;

			// We've get to fetch the grammar topic, so populate
			$.ajax({
				url: el[0].dataset.url,
				dataType: 'text',
				success: function(response) {
					el.append(response);
				},
				error: function(response) {
					el.append('Could not load this grammar topic -- please report this bug!');
				}
			});
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

	return View;
});
