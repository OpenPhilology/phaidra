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
				},
				failure: function(x, y, z) {
					console.log(x, y, z);
				}
			});
		},
		render: function() {
			return this;	
		},
		/*
		*	Converts data from flat JSON into hierarchical.
		*/
		convertData: function(words) {
			// Right now, our data comes in reverse. Delete this later.
			words = words.reverse();
			words = _.map(words, function(obj) {
				return _.pick(obj, 'tbwid', 'head', 'value');
			});

			var dataMap = words.reduce(function(map, node) {
				map[node.tbwid] = node;
				return map;
			}, {});

			// Create hierarchical data
			var treeData = [];
			words.forEach(function(node) {
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
			var margin = { top: 20, right: 120, bottom: 20, left: 120 },
				width = 960 - margin.right - margin.left,
				height = 800 - margin.top - margin.bottom;

			var i = 0, duration = 750;

			var tree = d3.layout.tree().size([height, width]);

			var diagonal = d3.svg.diagonal().projection(function(d) {
				return [d.x, d.y];
			});

			var svg = d3.select('.parse-tree').append('svg')
				.attr('width', width + margin.right + margin.left)
				.attr('height', height + margin.top + margin.bottom)
				.append('g')
				.attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

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
					.attr('r', 10)
					.on('click', click);

				nodeEnter.append('text')
					.attr('y', 20)
					.attr('dy', '.55em')
					.attr('text-anchor', 'middle')
					.text(function(d) {
						return d.value;
					})
					.style('fill-opacity', 1);

				var nodeUpdate = node.transition()
					.duration(duration)
					.attr('transform', function(d) {
						return 'translate(' + d.x + ', ' + d.y + ')';
					});

				// Transition exiting nodes to parents new position
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

					var siblings = (d.parent && d.parent.children) ? d.parent.children : [];

					for (var j = 0; j < siblings.length; j++) {
						if (d.id != siblings[j]["id"] && collide(d, siblings[j])) {
							console.log("collision detected!");
						}
					}

				});

				function collide(node, sibling) {
					var r = node.size,
						n1y1 = node.x - r,
						n1y2 = node.x + r;
					var r2 = sibling.size,
						n2y1 = sibling.x - r2,
						n2y2 = sibling.x + r2;

					return (n1y1 < n2y2 && n1y1 > n2y1) || (n1y2 > n2y2 && n1y2 < n2y1);
				}


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

						if (parent.tbwid == child.head) {
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
							update(parent);
							d3.selectAll('circle').each(function(d, i) {
								this.setAttribute('class', '');
							});
						}
					}
				}
			}
		}
	});

	return View;
});
