define(['jquery', 'underscore', 'backbone', 'models', 'collections', 'text!/templates/js/slide-info.html', 'daphne', 'morea', 'utils'], function($, _, Backbone, Models, Collections, Template, Daphne, Morea, Utils) {
	var View = Backbone.View.extend({
		tagName: 'div',
		className: 'slide-unit',
		template: _.template(Template),
		events: { 
			'click input': 'setFormData'
		},
		initialize: function(options) {
			this.options = options;

			// Decide whether we can draw right away or must wait
			if (this.model.get('populated'))
				this.draw();
			else
				this.model.on('populated', this.draw, this);
		},
		render: function() {
			return this;
		},
		draw: function() {
			var that = this;

			this.$el.html(this.template(this.model.attributes));
			this.$el.find('a[data-toggle="popover"]').popover();
			this.$el.find('em[data-toggle="tooltip"]').tooltip();

			// If there are any parse trees, render them
			// TODO: Make this more robust
			this.$el.find('[data-toggle="daphne"]').each(function(i, el) {
				var words = JSON.parse(el.innerHTML);
				el.innerHTML = '';

				el.addEventListener('submitted', that.submitTree.bind(that));
				el.addEventListener('completed', that.completeTree.bind(that));

				new Daphne(el, {
					data: words,
					mode: el.getAttribute('data-mode'),
					width: el.getAttribute('data-width') || 200,
					height: 400,
					initialScale: 0.9
				});
			});

			this.$el.find('[data-toggle="morea"]').each(function(i, el) {

				el.addEventListener('submitted', that.submitAlignment.bind(that));
				el.addEventListener('completed', that.completeAlignment.bind(that));

				new Morea(el, {
					mode: el.getAttribute('data-mode'),
					dataUrl: el.getAttribute('data-dataUrl'),
					targets: el.getAttribute('data-targets').split(","),
					langs: {
						"grc": {
							"hr": "Greek",
							"resource_uri": "",
							"dir": "ltr"
						},
						"en": {
							"hr": "English",
							"resource_uri": "",
							"dir": "ltr"
						}
					}
				});
			});

			return this;
		},
		submitTree: function(e) {
			this.model.set('starttime', new Date(this.$el.data('starttime')));
			this.model.set(e.detail);
			this.model.checkAnswer(this.model.get('response'));
		},
		completeTree: function(e) {
			this.model.set('starttime', new Date(this.$el.data('starttime')));
			this.model.set(e.detail);
			this.model.checkAnswer(this.model.get('response'));

			setTimeout(function() {
				$('.corner a').click();
			}, 2000);
		},
		submitAlignment: function(e) {
			this.model.set('starttime', new Date(this.$el.data('starttime')));
			this.model.set(e.detail);
			this.model.checkAnswer(this.model.get('response'));
		},
		completeAlignment: function(e) {
			this.model.set('starttime', new Date(this.$el.data('starttime')));
			this.model.set(e.detail);
			this.model.checkAnswer(this.model.get('response'));

			setTimeout(function() {
				$('.corner a').click();
			}, 2000);
		},
		setFormData: function(e) {
			this.model.set('starttime', new Date(this.$el.data('starttime')));
			var map = this.model.get('response') || {};
			this.$el.find('form input:checked').each(function(i, el) {
				map[el.getAttribute('name')] = el.getAttribute('value');
			});
			this.model.set('response', map);
			this.model.set('task', 'traditional_method_s' + _.last(window.location.pathname.split('/')));

			var attempt = {}, el = e.target;
			attempt[el.getAttribute('name')] = el.getAttribute('value');
			this.model.checkAnswer(attempt);
		}
	});

	return View;
});
