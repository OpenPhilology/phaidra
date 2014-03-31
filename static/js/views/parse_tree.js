define(['jquery', 'underscore', 'backbone', 'd3', 'bootstrap', 'text!templates/tree.html', 'jquery-ui'], function($, _, Backbone, d3, bootstrap, treeTemplate, jQueryUI) {
	var View = Backbone.View.extend({
		tagName: 'div',
		className: 'text',
		initialize: function(options) {
			var that = this;

			// Use the HTML 
			this.$el = $(this.options.container);
			this.$el.append(treeTemplate);

			// Make options available throughout view
			this.options = options;

			/*
				options.mode = edit | create | view
				1. Edit -- Editing existing parse tree
				2. Create -- Create new parse tree
				3. View -- Non-editable view of existing parse tree
			*/

			this.options.mode = this.$el.attr('data-mode');
			this.options.url = this.$el.attr('data-url'); 
			this.options.height = this.$el.attr('data-height') || '500';
			this.options.width = this.$el.attr('data-width') || '300';

			$.ajax({
				url: that.options.url,
				dataType: 'json', 
				success: function(sentence) {

					// Populate html
					var words = sentence.words;

					that.$el.find('.sentence').html("");
					for (var i = 0; i < words.length; i++) {
						that.$el.find('.sentence')
							.append('<span data-tbwid="' + words[i]["tbwid"] + '">' + words[i]["value"] + '</span> ');
					}

					if (that.options.mode == 'create') {
						that.$el.find('.panel-heading').append('<span class="badge point-tracker">0</span>');
					}

					data = that.convertData(words);
					that.renderTree(data);
					that.render();
				},
				failure: function(x, y, z) {
					console.log(x, y, z);
				}
			});
		},
		render: function() {
			var that = this;
			this.$el.find('select[name="pos"]').on('change', _.bind(this.displayFields, this));
			return this;	
		},
		/*
		*	Converts data from flat JSON into hierarchical.
		*/
		convertData: function(words) {
			var that = this;

			this.words = _.map(words, function(obj) {
				obj.width = (obj.value.length > obj.relation.length) ? obj.value.length : obj.relation.length;
				return _.pick(obj, 'tbwid', 'head', 'value', 'lemma', 'pos', 'person', 'number', 'tense', 'mood', 'voice', 'gender', 'case', 'degree', 'width', 'relation');
			});

			// If the student is creating the tree, then clone original data to check their answers later
			if (this.options.mode == 'create') {
				this.answers = JSON.parse(JSON.stringify(that.words));
				this.words = _.map(that.words, function(obj) {
					obj.pos = 'unassigned';
					return _.pick(obj, 'tbwid', 'value', 'head', 'width', 'pos');
				});
			}

			var dataMap = this.words.reduce(function(map, node) {
				map[node.tbwid] = node;
				return map;
			}, {});

			/* Append a root node to the tree:
			*  - For normal sentences, root has a tbwid of zero.
			*  - If it's a shortened sentence, the root node tbwid will not be zero.
			*/
			var rootNodeTbwid = 0;
			for (var i = 0; i < this.words.length; i++) {
				var node = this.words[i];
				if (dataMap[node.head] == undefined) {
					var rootNode = {
						'tbwid': node.head,
						'value': 'root',
						'pos': 'root'
					};
					that.words.push(rootNode);
					dataMap[node.head] = rootNode;
					rootNodeTbwid = node.head;
					break;
				}
			}
			if (this.options.mode == 'create') {
				this.words.forEach(function(node) {
					if (node.pos != 'root') node.head = rootNodeTbwid;
				});
				Object.keys(dataMap).forEach(function(tbwid) {
					if (dataMap[tbwid]["pos"] != 'root')
						dataMap[tbwid]["head"] = rootNodeTbwid;
				});
			}
			this.rootTbwid = rootNodeTbwid;

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
			this.dimensions = { 
				margin: { 
					top: 50, 
					right: 0, 
					bottom: 50, 
					left: 0 
				},
				width: this.$el.find('.tree-container').width(),
				height: this.options.height
			};

			var i = 0, duration = 500;
			var that = this;

			this.color = d3.scale.ordinal()
				.domain(["noun", "verb", "participle", "adj", "adverb", "particle", "conj", "prep", "pron", "numeral", "interjection", "exclam", "punct", "article", "root", "_", "unassigned"])
				.range(["#019292", "#D15241", "#8CD141", "#4E6087", "#8CD141", "#FF881A", "#754574", "#149069", "#523D5B", "#812F0F", "#F4BC78", "#F4BC78", "#1D78AA", "#257008", "#333", "#999", "#999"]);

			this.tree = d3.layout.tree().nodeSize([100, 50]);

			// Determine horizontal spacing needed for nodes based on their value or relation length, whichever is longer
			this.tree.separation(function(a, b) {
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

			this.svg = d3.select(this.$el.find('.tree-container')[0]).append('svg')
				.attr('class', 'svg-container');
			this.canvas = this.svg.append('g')
				.attr('class', 'canvas');
			this.canvas.append('g')
				.attr('transform', 'translate(' + ((that.dimensions.width / 2)) + ',' + that.dimensions.margin.top + ') scale(' + 0.9 + ')');

			// Set height on CSS element for height transition.
			this.$el.find('.svg-container').css('height', this.options.height + 'px');
			this.$el.find('.tree-container').css('max-height', this.options.height + 'px');

			// Only create the legend container for an SVG element one time.
			var legend = this.svg.append('g')
				.attr('class', 'legend')
				.attr('height', 100)
				.attr('width', 100)
				.attr('transform', 'translate(0, 10)');

			// Zooming and scale function for the SVG -- attached to actual object after update() function below.
			function zoom() {
				var scale = d3.event.scale,
					translation = d3.event.translate,
					tbound = -that.dimensions.height * scale,
					bbound = that.dimensions.height * scale,
					lbound = (-that.dimensions.width + that.dimensions.margin.right) * scale,
					rbound = (that.dimensions.width + that.dimensions.margin.left) * scale;

				var translation = [
					Math.max(Math.min(translation[0], rbound), lbound),
					Math.max(Math.min(translation[1], bbound), tbound)
				];

				that.canvas.attr('transform', 'translate(' + translation + ') scale(' + scale + ')');
			}

			this.root = treeData[0];
			update(this.root);

			/*
				Update function is called every time the structure of the tree changes. It manages adjusting the positioning of the nodes, 
				their colors, displaying attributes and relations, etc.
			*/
			function update(source) {

				var nodes = that.tree.nodes(that.root).reverse(),
					links = that.tree.links(nodes);

				nodes.forEach(function(d) {
					d.y = d.depth * 100;
				});

				var node = that.svg.select('.canvas g').selectAll('g.node')
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
					.style('stroke', function(d) {
						return that.color(d.pos);
					})
					.style('fill', function(d) {
						return '#FFF';
					})
					.on('click', click)
					.on('dblclick', editProps)
					.attr('class', function(d, i) {
						return (d.pos == 'root') ? 'root' : ''
					});

				nodeEnter.append('text')
					.attr('y', function(d, i) {
						if (d.pos == 'root') 
							return -30;
						else
							return 15;
					})
					.attr('dy', '14px')
					.attr('text-anchor', 'middle')
					.text(function(d) {
						return d.value;
					})
					.style('fill', function(d, i) {
						return (d.pos == 'root') ? '#CCC' : '#333';
					})
					.style('fill-opacity', 1);

				nodeEnter.append('text')
					.attr('y', function(d, i) {
						if (d.pos == 'root') 
							return '';
						else
							return -30;
					})
					.attr('dy', '12px')
					.attr('text-anchor', 'middle')
					.attr('class', 'label')
					.text(function(d) {
						return d.relation;
					});

				var nodeUpdate = node.transition()
					.duration(duration)
					.attr('transform', function(d) {
						return 'translate(' + d.x + ', ' + d.y + ')';
					});

				nodeUpdate.select('text.label')
					.text(function(d) {
						return d.relation;
					});

				nodeUpdate.select('circle')
					.style('stroke', function(d) {
						return that.color(d.pos);
					})
					.style('fill', function(d) {
						if (d3.select(this).classed('right'))
							return d3.rgb(that.color(d.pos)).brighter();
						else
							return '#FFF';
					})

				var link = that.svg.select('.canvas g').selectAll('path.link')
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

				nodes.forEach(function(d, i) {
					d.x0 = d.x;
					d.y0 = d.y;
				});

				// Get only unique colors for the legend -- temporary solution
				var legendNodes = [];
				_.each(nodes, function(n) {
					if (_.where(legendNodes, { pos: n.pos }).length == 0)
						legendNodes.push(n);	
				});
				legendNodes = _.sortBy(legendNodes, function(obj) {
					return obj.pos;
				});

				legend.selectAll('rect')
					.data(legendNodes, function(d, i) {
						return d.id || (d.id = ++i);
					})
					.enter()
					.append('rect')
					.attr('x', 15)
					.attr('y', function(d, i) {
						return i * 20;
					})
					.attr('width', 10)
					.attr('height', 10)
					.style('fill', function(d) {
						return that.color(d.pos);
					});

				legend.selectAll('text')
					.data(legendNodes, function(d, i) {
						return d.id || (d.id = ++i);
					})
					.enter()
					.append('text')
					.attr('x', 30)
					.attr('y', function(d, i) {
						return (i * 20) + 11;
					})
					.text(function(d) {
						return d.pos;
					});

				/*
					Handles what happens when node is double-clicked. Namely, a property editor pops up, which allows users to 
					update the properties of their trees.
				*/
				function editProps(d, i) {
					var modal = that.$el.find('.modal');
					modal.draggable({
						handle: '.modal-header'
					});

					modal.find('form')[0].reset();
					modal.find('form').eq(0).data('node', d);
					
					// Display values of the node -- REPLACE THIS with a template
					modal.find('.modal-header h4').html(d.value);
					modal.find('select[name="relation"] option[value="' + d.relation + '"]').prop('selected', true);
					modal.find('input[name="lemma"]').val(d.lemma || '');
					modal.find('select[name="pos"] option[data-morpheus="' + d.pos + '"]').prop('selected', true).change();
					modal.find('select[name="person"] option[data-morpheus="' + d.person + '"]').prop('selected', true);
					modal.find('select[name="number"] option[data-morpheus="' + d.number + '"]').prop('selected', true);
					modal.find('select[name="tense"] option[data-morpheus="' + d.tense + '"]').prop('selected', true);
					modal.find('select[name="mood"] option[data-morpheus="' + d.mood + '"]').prop('selected', true);
					modal.find('select[name="voice"] option[data-morpheus="' + d.voice + '"]').prop('selected', true);
					modal.find('select[name="gender"] option[data-morpheus="' + d.gender + '"]').prop('selected', true);
					modal.find('select[name="case"] option[data-morpheus="' + d.case + '"]').prop('selected', true);
					modal.find('select[name="degree"] option[data-morpheus="' + d.degree + '"]').prop('selected', true);

					modal.modal('show');
				}

				/*
					Handles what happens when a node is double clicked -- namely, it is selected in the parse tree
					and in the corresponding sentence.
				*/
				function click(d, i) {
					var c = d3.select(this);

					// If this node was previously selected, unselect it.
					if (c.classed('selected')) { 
						c.classed({ 'selected': false });
						that.$el.find('.sentence span[data-tbwid="' + d.tbwid + '"]').removeClass('selected');
						return;
					}
					else {
						c.classed({ 'selected': true });
					}

					// Highlight the word in the top sentence
						that.$el.find('.sentence span[data-tbwid="' + d.tbwid + '"]')
						.addClass('selected');

					// Check whether it's time to update links
					var selected = [];
					that.svg.selectAll('circle').each(function(d, i) {
						if (d3.select(this).classed('selected')) selected.push(d); 
					});

					// Means they've selected the new parent just now
					if (selected.length == 2) {
						var parent = d;
						var child = (parent.id != selected[0]["id"]) ? selected[0] : selected[1]; 

						if (parent.tbwid == child.head || child.pos == 'root') {

							that.svg.selectAll('circle').each(function(d, i) {
								d3.select(this).classed({ 'selected': false });
							});

							that.$el.find('.sentence span[data-tbwid="' + parent.tbwid + '"]')
								.removeClass('selected');

							that.$el.find('.sentence span[data-tbwid="' + child.tbwid + '"]')
								.removeClass('selected');
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

							// The problem area -- causes the children to get eaten? *Possible bug zone*
							if (child.parent.children.length == 0)
								delete child.parent.children;	

							child.parent = parent;
							child.head = parent.tbwid;
							update(child);
							update(parent);

							// Now, reset state of tree to unselected everything 
							that.svg.selectAll('circle').each(function(d, i) {
								d3.select(this).classed({ 'selected': false });
							});

							// Slow down, so users can see in the sentence which two words they connected
							setTimeout(function() {
								that.$el.find('.sentence span[data-tbwid="' + parent.tbwid + '"]').removeClass('selected');
								that.$el.find('.sentence span[data-tbwid="' + child.tbwid + '"]').removeClass('selected');
								that.checkConnection(child);
							}, 700);
						}
					}
				}
			}

			// Attach the zoom functionality to listen to the SVG object, although it *acts* upon the canvas group within.
			d3.select(that.$el.find('svg')[0])
				.call(d3.behavior.zoom()
					.scaleExtent([0.5, 5])
					.on("zoom", zoom))
				.on('dblclick.zoom', null);

			/*
				Update the POS and Morph attributes of a given node.
			*/
			function updateNodeAttrs(e) {
				e.preventDefault();
				var that = this;
				var node = that.$el.find('form').data('node');

				that.svg.selectAll('circle').each(function(d, i) {
					if (node.id == d.id) {
						var fields = that.$el.find('form .form-group:visible');	
						for (var i = 0; i < fields.length; i++) {
							var name, value;
							if ($(fields[i]).find('select').length == 1) {
								name = $(fields[i]).find('select');
								value = name.find(':selected').attr('data-morpheus') || name.find(':selected').attr('value') || '';
								name = name.prop('name');
							}
							else {
								name = $(fields[i]).find('input');
								value = name.val()
								name = name.prop('name');
							}

							// Now update the info in the original d3 data
							d[name] = value;

						}

						update(d);
					}
				});
				that.$el.find('.modal').modal('hide');
			}
			
			// Bind events
			this.$el.find('button[type="submit"]').on('click', _.bind(updateNodeAttrs, this));
			
			// Make update available outside this scope
			this.update = update;
		},
		/*
			Display only the correct fields that are appropriate to the node's POS.
		*/
		displayFields: function(e) {
			var form = this.$el.find('form');
			var formControls = form.find('.form-group');
			var pos = form.find('select[name="pos"]').val();

			for (var i = 0; i < formControls.length; i++) {
				var group = $(formControls[i]).attr('data-group');
				if (!group || group.indexOf(pos) == -1)
					$(formControls[i]).hide();
				else
					$(formControls[i]).show();
			}
		},
		/*
			Show whether a child node has been assigned to the correct parent, and update original dataset. 
			If all the nodes have been attached which don't belong to the root, check remaining root nodes.
		*/
		checkConnection: function(child) {
			// Don't check the connection unless the user is creating tree from scratch, 
			// because we wouldn't be checking against a gold-standard tree
			if (!this.options || this.options.mode != 'create') return;

			var that = this;
			var dataMap = this.answers.reduce(function(map, node) {
				map[node.tbwid] = node;
				return map;
			}, {});

			// Also check if the tree happens to be complete, dependency-wise -- morph done separately
			var complete = true;	

			// If the tree IS complete, mark the children still at the root as correct
			var rootChildren = [];
			var updateNodes = [];

			that.svg.selectAll('circle').each(function(d, i) {

				if (d.pos != 'root') {
					if (d.head == dataMap[d.tbwid]["head"])
						complete = complete ? true : false;
					else
						complete = false;

					if (d.head == that.rootTbwid) {
						rootChildren.push(this);
						updateNodes.push(d);
					}
				}

				if (d.id == child.id) {
					if (child.parent.tbwid != dataMap[child.tbwid]["head"]) {
						d3.select(this).classed({ 'right': false, 'wrong': true });
						that.update(child);
						console.log("WRONG ANSWER!")
					}
					else {
						d3.select(this).classed({ 'right': true, 'wrong': false });
						that.update(child);
						that.incrementPoints();
						console.log("Bravo!")
					}
				}
			});

			// Tree is complete, mark root children
			if (complete) {
				for (var i = 0; i < rootChildren.length; i++) {
					d3.select(rootChildren[i]).classed({ 'right': true, 'wrong': false });
					that.update(updateNodes);
					that.$el.find('span.point-tracker').html("COMPLETE!").addClass('bounce');
				}
				console.log("You completed the tree!!!!!!!!");
			}	
		},
		/*
			Very silly implementation to demonstrated how much fun it can be to Build Your Own Parse Tree!!
		*/
		incrementPoints: function(msg) {
			var pointTracker = this.$el.find('span.point-tracker');
			pointTracker.addClass('bounce');
			pointTracker.tooltip({
				title: function() {
					if (msg) return msg;

					var sayings = ["Smashing", "Superb", "Radical", "Fantastisch", "Excellent", "Prima", "Generic Encouragement"];
					var i = Math.floor((Math.random() * (sayings.length - 1)) + 1);
					return sayings[i] + '!';
				},
				placement: 'bottom',
				trigger: 'manual'
			});
			pointTracker.tooltip('show');
			var points = parseInt(this.$el.find('span.point-tracker').html()) + 1;
			this.$el.find('span.point-tracker').html(points);

			setTimeout(function() {
				pointTracker.tooltip('hide');
				pointTracker.removeClass('bounce')
			}, 1000);
		}
	});

	return View;
});
