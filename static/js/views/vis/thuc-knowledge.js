define(['jquery', 
	'underscore', 
	'backbone',
	'text!/templates/js/vis/thuc-knowledge.html'], 
	function($, _, Backbone, Template) { 

		return Backbone.View.extend({
			events: { },
			initialize: function(options) {
				_.bindAll(this, 'parseData');
				_.bindAll(this, 'displayError');

				var data = {
					"level": "book",
					"range": "urn:cts:greekLit:tlg0003.tlg001.perseus-grc",
					"user": USER
				};

				var that = this;
				$.ajax({
					url: '/api/v1/visualization/encountered/', 
					type: 'GET',
					data: data,
					success: that.parseData,
					error: that.displayError
				});
			},
			render: function() {
				return this;	
			},
			fullRender: function() {
				this.template = _.template(Template);
				this.$el.html(this.template({
					struct: this.struct
				}));
				this.$el.find('[data-toggle="tooltip"]').tooltip({
					html: true
				});
			},
			displayError: function(response) {
				this.$el.html("This user has not made any submissions yet.");
			},
			parseData: function(response) {
				this.struct = [];

				response.words.forEach(function(word) {
					this.placeWord(word, this.struct);
				}.bind(this));

				this.fullRender();
			},
			placeWord: function(word, struct) {
				var loc = word.CTS.split(':')[4].split('.');

				var book = loc[0];
				var chapter = loc[1];
				var sentence = loc[2];
				var index = parseInt(word.CTS.split(':')[5]);

				if (!struct[book])
					struct[book] = [];
				if (!struct[book][chapter])
					struct[book][chapter] = [];
				if (!struct[book][chapter][sentence])
					struct[book][chapter][sentence] = [];

				struct[book][chapter][sentence][index] = word;
			}
		});
	}
);
