function parse() {
	var that = this;
	var request = new XMLHttpRequest();
	var url = '/static/js/json/submissiondata.json';
	request.open('GET', url, true);

	request.onload = function() {
		if (request.status >= 200 && request.status < 400) {
			this.data = JSON.parse(request.responseText).objects;
			that.analyse(this.data);
			window.data = this.data;
		}
	}.bind(this);

	request.send();

	return this;
};

parse.prototype.analyse = function(objects) {
	var blacklist = ['139.18.40.135', '139.18.40.146', '139.18.40.154', '139.18.40.154', '139.18.40.167', '139.18.40.151', 'john', 'Mick', 'Ringo', 'Charlie'];

	var grouped = _.groupBy(objects, function(s) {
		if (blacklist.indexOf(s.user) === -1)
			return s.user;
		else
			return "blacklisted";
	});
	delete grouped.blacklisted;

	var trad = [], ag = [];

	// Figure out stuff based on submissions
	_.map(grouped, function(submissions, user) {
	
		var tasks = submissions.map(function(s) {
			return s.task;
		});

		if (tasks.indexOf('build_parse_tree') !== -1 || tasks.indexOf('align_sentence') !== -1) 
			ag.push({ "user": user, "submissions": submissions });
		if (tasks.indexOf('traditional_method_,module,0,section,0,slide,1') !== -1)
			trad.push({ "user": user, "submissions": submissions });
	});

	var Tcounts = [], Acounts = [];
	for (var i = 0, u; u = ag[i]; i++) {
		u.submissions = this.sortIntoSlides(u.submissions);
		u.slides = _.map(u.submissions, function(s) {
			return parseInt(s.slide) || undefined;
		});
		u.slides = _.uniq(u.slides).sort();
		Acounts = Acounts.concat(u.slides);
	}
	for (var i = 0, u; u = trad[i]; i++) {
		u.submissions = this.sortTradSlides(u.submissions);
		u.slides = _.map(u.submissions, function(s) {
			return parseInt(s.slide) || undefined;
		});
		u.slides = _.uniq(u.slides).sort();
		Tcounts = Tcounts.concat(u.slides);	
	}

	var TsortedBySlide = _.groupBy(Tcounts, function(c) {
		return c;
	});
	var AsortedBySlide = _.groupBy(Acounts, function(c) {
		return c;
	});
	delete TsortedBySlide["undefined"];
	delete AsortedBySlide["undefined"];

	var usersByTSlide = _.map(TsortedBySlide, function(y, x) {
		return { "slide": parseInt(x),"users": y.length };
	});
	var usersByASlide = _.map(AsortedBySlide, function(y, x) {
		return { "slide": parseInt(x),"users": y.length };
	});

	// Get percentage change to normalize numbers
	
	usersByTSlide = this.calcDelta(usersByTSlide);
	usersByASlide = this.calcDelta(usersByASlide);

	this.createLineChart(usersByTSlide, usersByASlide);
	this.createDifferenceChart(usersByTSlide, usersByASlide);

	window.A = this.calcTimeData(ag, "ag");
	window.T = this.calcTimeData(trad, "traditional");
};

parse.prototype.calcDelta = function(group) {
	for (var i = 0; i < group.length; i++) {
		var delta = 0;
		if (group[i-1]) {
			delta = group[i].users / group[i-1].users;	
		}
		if (delta !== 0)
			delta = (delta - 1);

		group[i].delta = delta;
	}
	return group;
};

parse.prototype.sortTradSlides = function(submissions) {
	var completed = [];
	var record = [];

	for (var i = 0, s; s = submissions[i]; i++) {
		var parts = s.task.split(',');

		if ((parts[4] === undefined || parts[6] === undefined) && (s.task !== 'build_parse_tree' && s.task !== 'align_sentence' && s.slideType !== 'slide_direct_select')) 
			console.log(s);
		if (typeof(parts[6]) !== 'undefined' && parseInt(parts[4]) !== 1 && typeof(parts[4]) !== 'undefined' && parseInt(parts[6]) !== 28 && parseInt(parts[6]) !== 24) {
			s.slide = parts[6];
			s.method = "traditional";
		}
	}

	return submissions;
};

parse.prototype.sortIntoSlides = function(submissions) {
	var completed = [];

	for (var i = 0, s; s = submissions[i]; i++) {

		var slide = 0;

		// Test cases
		//if (s.response.indexOf('"value":"The"') !== -1 || s.response.indexOf('"value":"γὰρ"') !== -1 || s.response.indexOf('"value":"οἵ"') !== -1 || s.response.indexOf('"value":"ἦλθον"') !== -1)
		//	slide = 'ambiguous'
		if (s.response.indexOf('"value":"apple"') !== -1 || s.response.indexOf('"value":"an"') !== -1 || s.response.indexOf('"value":"eats"') !== -1 || s.response.indexOf('"value":"man"') !== -1) 
			slide = '01'
		else if (s.response.indexOf('"value":"men"') !== -1 || s.response.indexOf('"value":"gods"') !== -1 || s.response.indexOf('"value":"all"') !== -1 || s.response.indexOf('"value":"watch"') !== -1)
			slide = '02'
		else if (s.response.indexOf('"value":"τρόπῳ"') !== -1 && s.response.indexOf('"id":4') !== -1)
			slide = '03'
		else if (s.response.indexOf('"value":"Ἀθηναῖοι"') !== -1 && s.response.indexOf('"id":3') !== -1)
			slide = '03'
		else if (s.response.indexOf('"value":"οἱ"') !== -1 && s.response.indexOf('"id":1') !== -1 && s.response.indexOf('"relation":"Atr"') !== -1)
			slide = '03'
		else if (s.response.indexOf('"value":"τοιῷδε"') !== -1)
			slide = '03'
		else if (s.response.indexOf('"value":"ἐπ\'"') !== -1 && s.response.indexOf('"id":39') !== -1) 
			slide = '04'
		else if (s.response.indexOf('"value":"οἴκου"') !== -1 && s.response.indexOf('"id":40') !== -1) 
			slide = '04'
		else if (s.response.indexOf('"value":"βασιλεὺς"') !== -1 || s.response.indexOf('"value":"Λεωτυχίδης"') !== -1 || s.response.indexOf('"value":"ἀπεχώρησεν"') !== -1)
			slide = '04'
		else if (s.response.indexOf('"value":"βραχέα"') !== -1 || s.response.indexOf('"value":"περιβόλου"') !== -1 || s.response.indexOf('"value":"τοῦ"') !== -1 || s.response.indexOf('"value":"εἱστήκει"') !== -1)
			slide = '09'
		else if (s.response.indexOf('"value":"πρεσβείᾳ"') !== -1 || s.response.indexOf('"value":"δὲ"') !== -1) 
			slide = '10'
		else if (s.response.indexOf('"value":"Λακεδαιμόνιοι"') !== -1 && s.response.indexOf('"id":1') !== -1) 
			slide = '10'
		else if (s.response.indexOf('"value":"ἀρχάς"') !== -1 || s.response.indexOf('"value":"οὐ"') !== -1 || s.response.indexOf('"value":"πρὸς"') !== -1 || s.response.indexOf('"value":"τὰς"') !== -1 || s.response.indexOf('"value":"προσῄει"') !== -1)
			slide = '13'
		else if (s.response.indexOf('"value":"Θεμιστοκλεῖ"') !== -1 || s.response.indexOf('"value":"φιλίαν"') !== -1 || s.response.indexOf('"value":"διὰ"') !== -1 || s.response.indexOf('"value":"αὐτοῦ"') !== -1 || s.response.indexOf('"value":"ἐπείθοντο"') !== -1)
			slide = '14'
		else if (s.response.indexOf('"value":"τῷ"') !== -1 && s.response.indexOf('"id":4') !== -1)
			slide = '14'
		else if (s.response.indexOf('"value":"Ἀθηναῖοι"') !== -1 && s.response.indexOf('"id":4') !== -1)
			slide = '17'
		else if (s.response.indexOf('"value":"πρέσβεις"') !== -1 && s.response.indexOf('"id":6') !== -1)
			slide = '17'
		else if (s.response.indexOf('"value":"τοὺς"') !== -1) 
			slide = '17'
		else if (s.response.indexOf('"value":"φανερὰν"') !== -1 || s.response.indexOf('"value":"ὀργὴν"') !== -1 || s.response.indexOf('"value":"Ἀθηναίοις"') !== -1 || s.response.indexOf('"value":"οὐκ"') !== -1 || s.response.indexOf('"value":"τοῖς"') !== -1)
			slide = '19'
		else if (s.response.indexOf('"value":"ἐπ\'"') !== -1 && s.response.indexOf('"id":6') !== -1)
			slide = '21'
		else if (s.response.indexOf('"value":"οἴκου"') !== -1 && s.response.indexOf('"id":7') !== -1)
			slide = '21'
		else if (s.response.indexOf('"value":"πρέσβεις"') !== -1 && s.response.indexOf('"id":3') !== -1)
			slide = '21'
		else if (s.response.indexOf('"value":"ἑκατέρων"') !== -1 || s.response.indexOf('"value":"ἀνεπικλήτως"') !== -1 || s.response.indexOf('"value":"ἀπῆλθον"') !== -1)
			slide = '21'
		else if (s.response.indexOf('"value":"Ἀθηναῖοι"') !== -1 && s.response.indexOf('"id":5') !== -1)
			slide = '22'
		else if (s.response.indexOf('"value":"ἐν"') !== -1 && s.response.indexOf('"id":9') !== -1)
			slide = '22'
		else if (s.response.indexOf('"value":"τούτῳ"') !== -1 && s.response.indexOf('"id":1') !== -1)
			slide = '22'
		else if (s.response.indexOf('"value":"τρόπῳ"') !== -1 && s.response.indexOf('"id":3') !== -1)
			slide = '22'
		else if (s.response.indexOf('"value":"οἱ"') !== -1 && s.response.indexOf('"id":4') !== -1)
			slide = '22'
		else if (s.response.indexOf('"value":"τῷ"') !== -1 && s.response.indexOf('"id":2') !== -1)
			slide = '22'
		else if (s.response.indexOf('"value":"πόλιν"') !== -1 || s.response.indexOf('"value":"τὴν"') !== -1 || s.response.indexOf('"value":"χρόνῳ"') !== -1 || s.response.indexOf('"value":"ὀλίγῳ"') !== -1)
			slide = '22'
		else if (s.response.indexOf('"value":"μάλιστα"') !== -1 || s.response.indexOf('"value":"προσέκειτο"') !== -1)
			slide = '23'
		else if (s.response.indexOf('"value":"ταῖς"') !== -1 || s.response.indexOf('"value":"ναυσὶ"') !== -1)
			slide = '25'
		else if (s.response.indexOf('"value":"τούτῳ"') !== -1 && s.response.indexOf('"id":2') !== -1)
			slide = '27'
		else if (s.response.indexOf('"value":"ἐν"') !== -1 && s.response.indexOf('"id":1') !== -1)
			slide = '27'
		else if (s.response.indexOf('"value":"Λακεδαιμόνιοι"') !== -1 && s.response.indexOf('"id":5') !== -1)
			slide = '27'
		else if (s.response.indexOf('"value":"Παυσανίαν"') !== -1 || s.response.indexOf('"value":"μετεπέμποντο"') !== -1)
			slide = '27'
		else if (s.encounteredWords) {
			s.encounteredWords.forEach(function(CTS) {
				if (CTS.indexOf('urn:cts:greekLit:tlg0003.tlg001.perseus-grc:1.89.1:') !== -1) {
					slide = '05';
				}
				else if (CTS.indexOf('urn:cts:greekLit:tlg0003.tlg001.perseus-grc:1.90.3:') !== -1) {
					slide = '06'; 
				}
				else if (CTS.indexOf('urn:cts:greekLit:tlg0003.tlg001.perseus-grc:1.102.1:') !== -1) {
					slide = '07';
				}
				else if (CTS.indexOf('urn:cts:greekLit:tlg0003.tlg001.perseus-grc:1.105.9:') !== -1) {
					slide = '08';
				}
				else if (CTS.indexOf('urn:cts:greekLit:tlg0003.tlg001.perseus-grc:1.103.5:') !== -1) {
					slide = '11';
				}
				else if (CTS.indexOf('urn:cts:greekLit:tlg0003.tlg001.perseus-grc:1.91.8:') !== -1) {
					slide = '12';
				}
				else if (CTS.indexOf('urn:cts:greekLit:tlg0003.tlg001.perseus-grc:1.93.1:') !== -1) {
					slide = '15';
				}
				else if (CTS.indexOf('urn:cts:greekLit:tlg0003.tlg001.perseus-grc:1.103.6:') !== -1) {
					slide = '16';
				}
				else if (CTS.indexOf('urn:cts:greekLit:tlg0003.tlg001.perseus-grc:1.104.1:') !== -1) {
					slide = '18';
				}
				else if (CTS.indexOf('urn:cts:greekLit:tlg0003.tlg001.perseus-grc:1.93.13:') !== -1) {
					slide = '20';
				}
				else if (CTS.indexOf('urn:cts:greekLit:tlg0003.tlg001.perseus-grc:1.94.1:') !== -1) {
					slide = '23';
				}
				else if (CTS.indexOf('urn:cts:greekLit:tlg0003.tlg001.perseus-grc:1.95.3:') !== -1) {
					slide = '24';
				}
				else if (CTS.indexOf('urn:cts:greekLit:tlg0003.tlg001.perseus-grc:1.105.1:') !== -1) {
					slide = '26';
				}
			});
		}

		if (slide !== 0 && (s.task === "build_parse_tree" || s.task === "align_sentence")) {
			completed.push(parseInt(slide));
			s.slide = slide;
			s.method = "ag";
		}
	}

	return submissions;

};

parse.prototype.createLineChart = function(usersByTSlide, usersByASlide) {
	var margin = { top: 20, right: 20, bottom: 30, left: 50 },
	width = 500 - margin.left - margin.right, 
	height = 250 - margin.top - margin.bottom;

	var x = d3.scale.linear().range([0, width]);
	var y = d3.scale.linear().range([height, 0]);

	var xAxis = d3.svg.axis()
		.scale(x)
		.orient("bottom");
	
	var yAxis = d3.svg.axis()
		.scale(y)
		.orient("left");
	
	var line = d3.svg.line()
		.x(function(d) {
			return x(d.slide);
		})
		.y(function(d) {
			return y(d.users);
		});
	
	var svg = d3.select('#raw-numbers').append('svg')
		.attr('width', width + margin.left + margin.right)
		.attr('height', height + margin.top + margin.bottom)
		.append('g')
			.attr('transform', 'translate(' + margin.left +',' + margin.top + ')');

	x.domain(d3.extent(usersByASlide, function(d) {
		return d.slide;
	}));
	y.domain(d3.extent(usersByTSlide, function(d) {
		return d.users;
	}));

	svg.append('g')
		.attr('class', 'x axis')
		.attr('transform', 'translate(0,' + height + ')')
		.call(xAxis)
	.append("text")
		.attr('y', 8)
		.attr('dy', '.71em')
		.style('text-anchor', 'end')
		.text('Slide');
	
	svg.append('g')
		.attr('class', 'y axis')
		.call(yAxis)
	.append("text")
		.attr('transform', 'rotate(-90)')
		.attr('y', -50)
		.attr('dy', '.71em')
		.style('text-anchor', 'end')
		.text('Users');
	
	svg.append('path')
		.datum(usersByASlide)
		.attr('class', 'line ag')
		.attr('d', line);

	svg.append('path')
		.datum(usersByTSlide)
		.attr('class', 'line trad')
		.attr('d', line);
};

parse.prototype.createDifferenceChart = function(T, A) {
	// Merge the data
	var data = A.map(function(a) {
		var t = T[a.slide - 1];

		return { 
			"slide": a.slide, 
			"a_delta": a.delta, 
			"t_delta": t ? t.delta : null, 
			"a_users": a.users, 
			"t_users": t ? t.users : null 
		};
	});
	window.delta = data;

	var margin = { top: 20, right: 20, bottom: 30, left: 50 },
	width = 500 - margin.left - margin.right, 
	height = 250 - margin.top - margin.bottom;

	var x = d3.scale.linear()
		.range([0, width]);

	var y = d3.scale.linear()
		.range([height, 0]);

	var xAxis = d3.svg.axis()
		.scale(x)
		.orient("bottom");

	var yAxis = d3.svg.axis()
		.scale(y)
		.orient("left");

	var line = d3.svg.area()
		.interpolate("basis")
		.x(function(d) { 
			return x(d.slide); 
		})
		.y(function(d) { 
			return y(d["a_delta"]); 
		});

	var area = d3.svg.area()
		.interpolate("basis")
		.x(function(d) { 
			return x(d.slide); 
		})
		.y1(function(d) { 
			return y(d["a_delta"]); 
		});

	var svg = d3.select("#difference-numbers").append("svg")
		.attr("width", width + margin.left + margin.right)
		.attr("height", height + margin.top + margin.bottom)
	  .append("g")
		.attr("transform", "translate(" + margin.left + "," + margin.top + ")");
	
	x.domain(d3.extent(data, function(d) { return d.slide; }));

	y.domain([
		d3.min(data, function(d) {
			return Math.min(d.a_delta, d.t_delta);
		}),
		d3.max(data, function(d) {
			return Math.max(d.a_delta, d.t_delta);
		})
	]);

	svg.datum(data);
	svg.append("clipPath")
	  .attr("id", "clip-below")
	.append("path")
	  .attr("d", area.y0(height));

	svg.append("clipPath")
	  .attr("id", "clip-above")
	.append("path")
	  .attr("d", area.y0(0));

	svg.append("path")
	  .attr("class", "area above")
	  .attr("clip-path", "url(#clip-above)")
	  .attr("d", area.y0(function(d) { 
		// Because after slide 24 we don't have trad data, so no diff is valid
		return d.t_delta ? y(d["t_delta"]) : y(d.a_delta); 
	}));

	svg.append("path")
	  .attr("class", "area below")
	  .attr("clip-path", "url(#clip-below)")
	  .attr("d", area);

	svg.append("path")
	  .attr("class", "line")
	  .attr("d", line);

	svg.append("g")
	  .attr("class", "x axis")
	  .attr("transform", "translate(0," + height + ")")
	  .call(xAxis)
	.append("text")
		.attr('y', 8)
		.attr('dy', '.71em')
		.style('text-anchor', 'end')
		.text('Slide');

	svg.append('g')
		.attr('class', 'y axis')
		.call(yAxis)
	.append("text")
		.attr('transform', 'rotate(-90)')
		.attr('y', -50)
		.attr('dy', '.71em')
		.style('text-anchor', 'end')
		.text('Delta');
	
	this.fillTables(data);
};

parse.prototype.fillTables = function(data) {
	// Fill the Difference Table
	data.forEach(function(d) {
		var row = document.createElement('tr');
		row.innerHTML += '<td>' + d.slide + '</td>';
		row.innerHTML += '<td>' + d.t_users + '</td>';
		row.innerHTML += '<td>' + parseFloat(d.t_delta).toFixed(3) + '</td>';
		row.innerHTML += '<td>' + d.a_users + '</td>';
		row.innerHTML += '<td>' + parseFloat(d.a_delta).toFixed(3) + '</td>';

		var bg = d.a_delta > d.t_delta ? 'ag-light' : 'trad-light';
		bg = d.a_delta === d.t_delta ? '' : bg;
		bg = (!d.t_delta && d.t_delta != 0) ? '' : bg;
		row.className = bg;

		document.querySelector('#difference-table tbody').appendChild(row);
	});

	data.forEach(function(d) {
		var row = document.createElement('tr');
		row.innerHTML += '<td>' + d.slide + '</td>';
		row.innerHTML += '<td>' + d.t_users + '</td>';
		row.innerHTML += '<td>' + d.a_users + '</td>';

		document.querySelector('#raw-numbers-table tbody').appendChild(row);
	});
};

parse.prototype.calcTimeData = function(data, method) {
	// Get a list of submissions
	var subs = data.map(function(d) {
		return d.submissions;
	});
	subs = _.flatten(subs);
	subs.filter(function(s) {
		return s.method === method;
	});

	// Group by user
	var users = _.groupBy(subs, function(s) {
		return s.user;
	});
	
	var map = {};
	_.forEach(users, function(submissions, user) {
		var groups = _.groupBy(submissions, function(s) {
			return parseInt(s.slide);
		});
		delete groups["NaN"];
		_.forEach(groups, function(subs, key) {
			var s = _.pluck(subs, 'timestamp').sort();
			var start = new Date(s[0]);
			var end = new Date(s[s.length - 1]);
			var diff = end - start;
			(map[key] || (map[key] = [])).push(parseFloat((diff / 1000) / 60).toFixed(2) + "m");	
		});
	});
	// Times that each user spent on each slide
	window.map = map;

	return subs;
};

new parse();
