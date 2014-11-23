define(['jquery', 'underscore', 'backbone', 'd3'], function($, _, Backbone, d3) { 

		var View = Backbone.View.extend({
			events: { },
			initialize: function(options) {
				var s = options.statistics;

				this.drawDonut('#syn', (s.syntax), '#D15241', 'Syntax'); 		
				this.drawDonut('#morph', (s.morphology), '#1FADAD', 'Morphology'); 		
				this.drawDonut('#vocab', (s.vocab), '#f4bc78', 'Vocabulary'); 		
			},
			render: function() {
				return this;	
			},
			drawSparkline: function(selector, data, color) {
				var graph = d3.select(selector).append('svg')
					.attr('width', 50)
					.attr('height', 15);

				var x = d3.scale.linear().domain([0, 10]).range([0, 50]);
				var y = d3.scale.linear().domain([0, 10]).range([0, 15]);

				var line = d3.svg.line()
					.x(function(d, i) {
						return x(i);
					})
					.y(function(d, i) {
						return y(d);
					});

				graph.append('svg:path').attr('d', line(data));
			},
			drawDonut: function(selector, percentComplete, color, label) {
				selector += ' .pie';
				$(selector).html("");

				var width = 100,
					height = 100,
					radius = (width + height) / 2, 
					padding = 10;

				var colors = d3.scale.ordinal()
					.domain(["complete", "incomplete"])
					.range([color, '#DEDEDE']);

				var values = [
					{ key: "complete", value: percentComplete },
					{ key: "incomplete", value: 100 - percentComplete }
				];

				var arc = d3.svg.arc()
					.outerRadius(function(d) {
						return d.data.key == "complete" ? 53 : 50;
					})
					.innerRadius(function(d) {
						return d.data.key == "complete" ? 37 : 40;
					});

				var pie = d3.layout.pie()
					.sort(null)
					.value(function(d) {
						return d.value;
					});

				var svg = d3.select(selector).append('svg')
					.attr('width', width + 20)
					.attr('height', height + 20)
					.append('g')
					.attr('transform', 'translate(60, 60)');

				var g = svg.selectAll('.arc')
					.data(pie(values))
					.enter();

				var group = g.append('g')
					.attr('class', 'arc');

				var path = g.append('path')
					.attr('d', arc)
					.style('fill', function(d) {
						return colors(d.data.key);
					})
					.style('fill-opacity', 0.8);

				svg.append('text')
					.attr('dy', '.35em')
					.style('text-anchor', 'middle')
					.text(percentComplete.toFixed(0) + '%');

			}
		});

	return View;
});
