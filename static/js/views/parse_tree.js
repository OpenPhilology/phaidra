define(['jquery', 'underscore', 'backbone', 'd3'], function($, _, Backbone, d3) {
	var View = Backbone.View.extend({
		tagName: 'div',
		className: 'text',
		events: {
		},
		initialize: function(options) {
			this.$el = $('');
			var that = this;
			$.ajax({
				url: '/api/sentence/3602/?format=json',
				dataType: 'json', 
				success: function(sentence) {

					// Populate html
					options.container.find('.sentence').html(sentence.sentence);

					data = that.convertData(sentence.words);
					that.renderTree(data);
					that.render();
				},
				failure: function(x, y, z) {
					console.log(x, y, z);
				}
			});
		},
		render: function() {
			$('.svg-container').parent().append('<a id="zoom-in" href="#" class="btn btn-default">+</a> <a id="zoom-out" href="#" class="btn btn-default">-</a>');
			return this;	
		},
		/*
		*	Converts data from flat JSON into hierarchical.
		*/
		convertData: function(words) {
			// Right now, our data comes in reverse. Delete this later.
			this.words = words.reverse();
			this.words = _.map(words, function(obj) {

				// Just to start the tree from scratch
				obj.head = 0;

				// Assign a width for building the tree later
				obj.width = obj.value.length;

				return _.pick(obj, 'tbwid', 'head', 'value', 'width');
			});

			// Create a root node
			this.words.push({ 'tbwid': 0, 'value': 'root'});

			var dataMap = this.words.reduce(function(map, node) {
				map[node.tbwid] = node;
				return map;
			}, {});

			// Create hierarchical data
			var treeData = [];
			this.words.forEach(function(node) {
				var head = dataMap[node.head];
				if (head) 
					(head.children || (head.children = [])).push(node);
				else 
					treeData.push(node);
			});
			return treeData;
		},
		/*
		*	Renders the parse tree
		*/
		renderTree: function(treeData) {
			var margin = { top: 30, right: 0, bottom: 30, left: 0 },
				width = $('.parse-tree').width(),
				height = 500 - margin.top - margin.bottom;

			var i = 0, duration = 750;
			var that = this;

			var tree = d3.layout.tree().nodeSize([100, 50]);
			tree.separation(function(a, b) {

				// Determine horizontal spacing needed for words based on their length
				var max = _.max(that.words, function(obj) {
					return obj.width;
				}).width + 1;
				var widths = [.2], scale = .13;
				for (j = 1; j < max; j++)
					widths.push(parseFloat(widths[j-1]) + scale);

				var avg = Math.ceil((a.width + b.width) / 2);
				return widths[avg];
			});

			var diagonal = d3.svg.diagonal().projection(function(d) {
				return [d.x, d.y];
			});

			var svg = d3.select('.parse-tree').append('svg')
				.attr('class', 'svg-container')
				.style('overflow', 'scroll')
			.append('g')
				.attr('class', 'canvas')
			.append('g')
				.attr('transform', 'translate(' + (width / 2) + ',' + margin.top + ')')


			function zoom() {
				var scale = d3.event.scale,
					translation = d3.event.translate,
					tbound = -height * scale,
					bbound = height * scale,
					lbound = (-width + margin.right) * scale,
					rbound = (width + margin.left) * scale;

				translation = [
					Math.max(Math.min(translation[0], rbound), lbound),
					Math.max(Math.min(translation[1], bbound), tbound)
				];
				d3.select('.canvas')
					.attr('transform', 'translate(' + translation + ') scale(' + scale + ')');
			}

			root = treeData[0];
			update(root);

			function update(source) {
				var nodes = tree.nodes(root).reverse(),
					links = tree.links(nodes);

				nodes.forEach(function(d) {
					d.y = d.depth * 100;
				});

				var node = svg.selectAll('g.node')
					.data(nodes, function(d) {
						return d.id || (d.id = ++i);
					});

				var nodeEnter = node.enter().append('g')
					.attr('class', 'node')
					.attr('transform', function(d) {
						return 'translate(' + source.x + ', ' + source.y + ')';
					});

				nodeEnter.append('circle')
					.attr('r', function(d, i) {
						return (d.tbwid == 0) ? 5 : 10;
					})
					.on('click', click)
					.attr('class', function(d, i) {
						return (d.tbwid == 0) ? 'root' : ''
					});

				nodeEnter.append('text')
					.attr('y', function(d, i) {
						if (d.tbwid == 0) 
							return -30;
						else
							return 20;
					})
					.attr('dy', '14px')
					.attr('text-anchor', 'middle')
					.text(function(d) {
						return d.value;
					})
					.style('fill', function(d, i) {
						return (d.tbwid == 0) ? '#CCC' : '#333';
					})
					.style('fill-opacity', 1);

				var nodeUpdate = node.transition()
					.duration(duration)
					.attr('transform', function(d) {
						return 'translate(' + d.x + ', ' + d.y + ')';
					});

				var nodeExit = node.exit().transition()
					.duration(duration)
					.attr('transform', function(d) {
						return 'translate(' + source.x + ',' + source.y + ')';
					})
					.remove();

				nodeExit.select('circle')
					.attr('r', 1e-6);

				nodeExit.select('text')
					.style('fill-opacity', 1e-6);

				var link = svg.selectAll('path.link')
					.data(links, function(d) {
						return d.target.id;
					});

				link.enter().insert('path', 'g')
					.attr('class', 'link')
					.attr('d', function(d) {
						var o = { x: source.x, y: source.y };
						return diagonal({ source: o, target: o });
					});

				link.transition()
					.duration(duration)
					.attr('d', diagonal);

				link.exit().transition()
					.duration(duration)
					.attr('d', function(d) {
						var o = { x: source.x, y: source.y};
						return diagonal({ source: o, target: o });
					})
					.remove();

				nodes.forEach(function(d, i) {
					d.x0 = d.x;
					d.y0 = d.y;
				});

				function click(d, i) {
					var c = d3.select(this);

					// If this node was previously selected, unselect it.
					if (c.classed('selected')) { 
						this.setAttribute('class', '');
						return;
					}
					else
						c.attr('class', 'selected');

					// Check whether it's time to update links
					var selected = [];
					d3.selectAll('circle').each(function(d, i) {
						if (d3.select(this).classed('selected')) selected.push(d); 
					});

					// Means they've selected the new parent just now
					if (selected.length == 2) {
						var parent = d;
						var child = (parent.id != selected[0]["id"]) ? selected[0] : selected[1]; 

						if (parent.tbwid == child.head || child.tbwid == 0) {
							d3.selectAll('circle').each(function(d, i) {
								this.setAttribute('class', '');
							});
						}
						else {
							(parent.children || (parent.children = [])).push(child);
							parent.children = _.sortBy(parent.children, function(obj) {
								return obj.tbwid;
							});

							// Remove child from former parent
							child.parent.children = _.filter(child.parent.children, function(obj) {
								return obj.id != child.id;
							});
							if (child.parent.children.length == 0)
								delete child.parent.children;	

							child.parent = parent;
							child.head = parent.twid;
							update(child);
							//update(parent);
							d3.selectAll('circle').each(function(d, i) {
								this.setAttribute('class', '');
							});
						}
					}
				}

				d3.select('svg').call(d3.behavior.zoom()
						.scaleExtent([0.5, 5])
						.on("zoom", zoom));
			}
		}
	});

	return View;
});
