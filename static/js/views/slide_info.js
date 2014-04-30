define(['jquery', 'underscore', 'backbone', 'models', 'collections', 'views/parse_tree'], function($, _, Backbone, Models, Collections, parseTreeView) {
	var View = Backbone.View.extend({
		tagName: 'div',
		className: 'slide-unit',
		events: {
			//"click .btn-continue": "navigate"
		},
		initialize: function(options) {

			var that = this;

			/*
			View takes either a Slide model or a path to a simple HTML page 
			*/
			if (this.model.get('includeHTML')) {
				$.ajax({
					url: that.model.get('includeHTML'),
					type: 'GET',
					async: false,
					success: function(responseText) {
						that.template = _.template(responseText);
						that.$el.html(that.template(that.model.attributes));

						that.$el.find('a[data-toggle="popover"]').popover();
						that.$el.find('em[data-toggle="tooltip"]').tooltip();

					},
					error: function(responseText) {
						console.log("Problem!");	
					}
				});
			}
			else {
				this.template(this.model.attributes);
			}

			var tableView;
			if (this.$el.find('.inflection-placeholder').length > 0) {
				tableView = new inflectionTableView().render({
					el: this.$el.find('.inflection-placeholder')
				});
			}

			if (this.$el.find('.parse-tree').length > 0) {
				parseTree = new parseTreeView({ container: that.$el.find('.parse-tree')}).render();				
			}
		},
		render: function() {
			return this;
		},
		navigate: function(e) {
			e.preventDefault();

			// Try not to laugh -- this will be fixed
			//var url = Backbone.history.fragment.split('/').splice(0, 5).join('/') + '/' + (this.model.get('index') + 1);

			//Backbone.history.navigate(url, { trigger: true });
		}
	});

	return View;
});
