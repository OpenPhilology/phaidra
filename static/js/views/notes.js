define(['jquery', 'underscore', 'backbone', 'utils', 'views/notes-about-word', 'views/notes-translations', 'views/notes-about-sentence', 'views/notes-user-annotations', 'views/notes-translate', 'views/notes-build-parse-tree', 'text!/templates/js/notes.html'], function($, _, Backbone, Utils, AboutWordView, TranslationsView, AboutSentenceView, UserAnnotationsView, TranslateView, BuildParseTreeView, Template) { 

	var View = Backbone.View.extend({
		tagName: 'div', 
		className: 'col-md-12 notes',
		template: _.template(Template),
		events: { 
			'click #reader-menu a': 'navigate',
			'click .parse-tree-view': 'showParseTree'
		},
		initialize: function(options) {
			this.options = options;	
			this.model.words.bind('change:selected change:hovered', this.toggleNotes, this);

			// Contains references to our subviews
			this.views = [];
		},
		render: function() {
			this.$el.html(Template);
			return this;	
		},
		navigate: function(e) {

			// 'About' button has span inside, so need to select its parent sometimes
			e.target = (e.target.tagName === 'A') ? e.target : e.target.parentElement;
			var target = e.target.dataset.target;
			var els = this.$el.find('div[data-source]');

			$.each(els, function(i, el) {
				if (el.dataset.source === target)
					$(el).show();
				else 
					$(el).hide();
			});

			this.$el.find('#reader-menu li').removeClass('active');
			$(e.target.parentElement).addClass('active');
			this.renderSubview(target);
		},
		makeView: function(view, options) {
			switch (view) {
				case 'about-word':
					return new AboutWordView(options);
				case 'about-sentence':
					return new AboutSentenceView(options);
				case 'user-annotations':
					return new UserAnnotationsView(options);
				case 'translate':
					return new TranslateView(options);
				case 'build-parse-tree':
					return new BuildParseTreeView(options);
				case 'translations':
					return new TranslationsView(options);
				default:
					console.log("didn't find this view");
			}
		},
		renderSubview: function(view, options) {
			var selected = this.model.words.findWhere({ selected: true });

			// Renders the appropriate subview
			var subrender = function() {
				
				// Give the user the definite article with the definition
				if (selected.get('pos') == 'noun') {
					selected.set('article', Utils.getDefiniteArticle(selected.get('gender')));
				}

				var options = {
					el: this.$el.find('div[data-source="' + view + '"]'),
					model: selected,
					langs: _.uniq(_.pluck(selected.get('translations'), 'lang')),
					lang: this.lang || locale.split('-')[0], 	// Locale is set in base.html, comes from Django. 
					grammar: selected.getGrammar()
				};

				this.makeView(view, options).render();
				this.$el.addClass('expanded');

			}.bind(this);

			// Fetch word's details, or if we've fetched them before, simply display
			if (selected.get('translated'))
				subrender();
			else 
				selected.fetch({ success: subrender });

		},
		toggleNotes: function(model) {
			if (model.get('hovered') && !model.get('selected') && 
				(this.model.words.findWhere({ selected: true }) == undefined)) {
				this.$el.find('.intro').html(
					gettext('Information about') + ' <span lang="' + model.get('lang') +'">' + model.get('value') + '</span>'
				);
				this.$el.removeClass('expanded');
				this.$el.find('.notes-nav a').eq(1).attr('title', 'Hide Resources');
			}

			// This will perform a fetch on the model for full data
			else if (model.get('selected') && !model.get('translated')) {
				this.$el.find('.notes-nav a').eq(1).attr('title', gettext('Show Resources'));
				this.renderSubview('about-word');
			}

		},
		collapseNotes: function(e) {
			e.preventDefault();
			var selected = this.model.words.findWhere({ selected: true });
			if (typeof(selected) != 'undefined')
				selected.set('selected', false);
		},
		/*showParseTree: function(e) {
			e.preventDefault();

			var selectedWord = this.model.words.findWhere({ selected: true });
			var sentence = this.model.words.where({ sentenceCTS: selectedWord.get('sentenceCTS') });
			var words = sentence.map(function(el, i) {
				el.attributes.id = el.attributes.tbwid;
				return el.attributes;
			});

			new Daphne('[data-toggle="daphne"]', {
				data: words,
				mode: 'edit',
				height: 600,
				width: 1000,
				initialScale: 0.9
			});

			$('.modal').modal('show');
		}*/
	});

	return View;

});
