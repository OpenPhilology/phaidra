define(['jquery', 'underscore', 'backbone', 'd3', 'bootstrap', 'jquery-ui'], function($, _, Backbone, d3, bootstrap) {
	var View = Backbone.View.extend({
		tagName: 'div',
		className: 'text',
		initialize: function(options) {
			this.$el = $('');
			var that = this;

			this.options = options;

			/*
				options.mode = edit | create | display
				1. Edit -- Editing existing parse tree
				2. Create -- Create new parse tree
				3. Display -- Non-editable view of existing parse tree
			*/

			// To test answer checking!
			//this.options.mode = 'create';

			$.ajax({
				// Shortened sentence example:
				//url: '/api/sentence/get_one_random_short/?format=json&lemma=κρατέω&tense=aor&voice=act&mood=ind&tbwid=48',

				// Full sentence example:
				url: '/api/sentence/get_one_random/?format=json&number=pl&case=nom&lemma=οἰκία',

				dataType: 'json', 
				success: function(sentence) {

					// Populate html
					var words = sentence.words;

					for (var i = 0; i < words.length; i++) {
						options.container.find('.sentence')
							.append('<span data-tbwid="' + words[i]["tbwid"] + '">' + words[i]["value"] + '</span> ');
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
			$('select[name="pos"]').on('change', that.displayFields);
			$('button[type="submit"]').on('click', that.updateNodeAttrs);
			return this;	
		},
		/*
		*	Converts data from flat JSON into hierarchical.
		*/
		convertData: function(words) {
			var that = this;

			this.words = _.map(words, function(obj) {
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

			var i = 0, duration = 600;
			var that = this;

			var color = d3.scale.ordinal()
				.domain(["noun", "verb", "participle", "adj", "adverb", "particle", "conj", "prep", "pron", "numeral", "interjection", "exclam", "punct", "article", "root", "", "unassigned"])
				.range(["#4E6087", "#D15241", "#999", "#1FADAD", "#F05629", "#FF881A", "#931926", "#49A556", "#523D5B", "#999", "#F4BC78", "#F4BC78", "#999", "#6EE2E2", "#333", "#666", "#999"]);

			var tree = d3.layout.tree().nodeSize([100, 50]);

			// Determine horizontal spacing needed for words based on their length
			tree.separation(function(a, b) {
				var max = _.max(that.words, function(obj) {
					return obj.value.length;
				}).value.length + 1;
				var widths = [.2], scale = .13;
				for (j = 1; j < max; j++)
					widths.push(parseFloat(widths[j-1]) + scale);

				var avg = Math.ceil((a.value.length + b.value.length) / 2);
				return widths[avg];
			});

			var diagonal = d3.svg.diagonal().projection(function(d) {
				return [d.x, d.y];
			});

			var svg = d3.select('.parse-tree').append('svg')
				.attr('class', 'svg-container')
				.style('overflow', 'scroll')
				.style('height', '700px')
			.append('g')
				.attr('class', 'canvas')
			.append('g')
				.attr('transform', 'translate(' + (width / 2) + ',' + margin.top + ')')

			var legend = d3.select('.svg-container').append('g')
				.attr('class', 'legend')
				.attr('height', 100)
				.attr('width', 100)
				.attr('transform', 'translate(0, 10)');

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
						return (d.pos == 'root') ? 5 : 10;
					})
					.style('stroke', function(d) {
						return color(d.pos);
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

				// Get only unique colors for the legend
				var legendNodes = [];
				_.each(nodes, function(n) {
					if (_.where(legendNodes, { pos: n.pos }).length == 0)
						legendNodes.push(n);	
				});

				legend.selectAll('rect')
					.data(legendNodes, function(d, i) {
						return d.id || (d.id = ++i);
					})
					.enter()
					.append('rect')
					.attr('x', 10)
					.attr('y', function(d, i) {
						return i * 20;
					})
					.attr('width', 10)
					.attr('height', 10)
					.style('fill', function(d) {
						return color(d.pos);
					});

				legend.selectAll('text')
					.data(legendNodes, function(d, i) {
						return d.id || (d.id = ++i);
					})
					.enter()
					.append('text')
					.attr('x', 23)
					.attr('y', function(d, i) {
						return (i * 20) + 9;
					})
					.text(function(d) {
						return d.pos;
					});

				function editProps(d, i) {
					var modal = $('#parse-tree-modal');
					modal.draggable({
						handle: '.modal-header',
						backdrop: false
					});

					modal.find('form')[0].reset();
					modal.find('form').eq(0).data('node', d);
					
					// Display values of the node -- replace this with a template
					modal.find('.modal-header h4').html(d.value);
					modal.find('select[name="relation"] option[value="' + d.relation + '"]').prop('selected', true);
					modal.find('input[name="lemma"]').val(d.lemma || '');
					modal.find('select[name="pos"] option[data-morpheus="' + d.pos + '"]').prop('selected', true).trigger('change');
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

				function click(d, i) {
					var c = d3.select(this);

					// If this node was previously selected, unselect it.
					if (c.classed('selected')) { 
						this.classList.remove('selected');
						that.options.container
							.find('.sentence span[data-tbwid="' + d.tbwid + '"]')
							.removeClass('selected');

						return;
					}
					else {
						/* CAUSES PROBLEM IN SAFARI 6.0.3, though caniuse.com says it shouldn't... */
						this.classList.add('selected');
					}

					// Highlight the word in the top sentence
					that.options.container
						.find('.sentence span[data-tbwid="' + d.tbwid + '"]')
						.addClass('selected');

					// Check whether it's time to update links
					var selected = [];
					d3.selectAll('circle').each(function(d, i) {
						if (d3.select(this).classed('selected')) selected.push(d); 
					});

					// Means they've selected the new parent just now
					if (selected.length == 2) {
						var parent = d;
						var child = (parent.id != selected[0]["id"]) ? selected[0] : selected[1]; 

						if (parent.tbwid == child.head || child.pos == 'root') {
							d3.selectAll('circle').each(function(d, i) {
								this.classList.remove('selected');
							});

							that.options.container
								.find('.sentence span[data-tbwid="' + parent.tbwid + '"]')
								.removeClass('selected');

							that.options.container
								.find('.sentence span[data-tbwid="' + child.tbwid + '"]')
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

							// The problem area -- causes the children to get eaten

							/*if (child.parent.children.length == 0)
								delete child.parent.children;	
							*/

							child.parent = parent;
							child.head = parent.twid;
							update(child);
							update(parent);

							// Now, reset state of tree to unselected everything 
							d3.selectAll('circle').each(function(d, i) {
								this.classList.remove('selected');
							});

							// So users can see in the sentence which two words they connected
							setTimeout(function() {
								that.options.container.find('.sentence span[data-tbwid="' + parent.tbwid + '"]').removeClass('selected');
								that.options.container.find('.sentence span[data-tbwid="' + child.tbwid + '"]').removeClass('selected');
								/* Check whether the connection is correct 
									-- If it's incorrect if the child has the wrong parent
									-- Do connection check after the node has already been moved 
								*/
								that.checkConnection(child);
							}, 700);
						}
					}
				}

				d3.select('svg').call(d3.behavior.zoom()
						.scaleExtent([0.5, 5])
						.on("zoom", zoom))
						.on('dblclick.zoom', null);
			}
		},
		displayFields: function(e) {
			var form = $('form');
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
		updateNodeAttrs: function(e) {
			e.preventDefault();
			var node = $($('form').eq(0)).data('node');

			d3.selectAll('circle').each(function(d, i) {
				if (node.id == d.id) {
					
				}
			});
		},
		checkConnection: function(child) {
			// Don't check the connection unless the user is creating tree from scratch, 
			// because we wouldn't be checking against a gold-standard tree
			if (!this.options || this.options.mode != 'create') return;

			var dataMap = this.answers.reduce(function(map, node) {
				map[node.tbwid] = node;
				return map;
			}, {});

			d3.selectAll('circle').each(function(d, i) {
				if (d.id == child.id) {
					if (child.parent.tbwid != dataMap[child.tbwid]["head"]) {
						this.classList.remove('right');
						this.classList.add('wrong');
						console.log("WRONG ANSWER!")
					}
					else {
						this.classList.remove('wrong');
						this.classList.add('right');
						console.log("Bravo!")
					}
				}
			});
		}
	});

	return View;
});
