// Namespacing

Phaidra.Views.ProgressViz = Backbone.View.extend({
	tagName: 'div',
	className: 'progress-viz',
	initialize: function() {

		// Create placeholder data
		var that = this;
		this.work = [];

		for (var i = 0; i < 8; i++) {
			that.work.push(
				{
					'book': i,
					'chapters': Math.floor((Math.random() * 10) + 5),
					'chapter': []
				}
			);
			
			for (var j = 0; j < Math.floor(Math.random() * 120) + 100; j++) {
				that.work[i].chapter.push([
					Math.floor(Math.random() * 10) + 5,		// red
					Math.floor(Math.random() * 10) + 5,		// green
					Math.floor(Math.random() * 10) + 5,		// blue
					Math.floor(Math.random() * 10) + 5		// rest
				]);
			}
		}

		console.log(that.work);

	},
	render: function() {
		
		var that = this;
		window.work = this.work;

		var work = this.work;

		// for each book in the work
		for (var i = 0; i < work.length; i++) {
			
			var line = '';

			// for each chapter in each book
			for (var j = 0; j < work[i].chapter.length; j++) {

				for (var k = 0; k < work[i].chapter[j][0]; k++)
					line += '<span class="r"></span>'
				for (var k = 0; k < work[i].chapter[j][1]; k++)
					line += '<span class="g"></span>'
				for (var k = 0; k < work[i].chapter[j][2]; k++)
					line += '<span class="b"></span>'
				for (var k = 0; k < work[i].chapter[j][3]; k++)
					line += '<span></span>'
				
				line += '<Br>';
			}
			that.$el.find('.book' + (i + 1)).html(line);
		}
	}
});
