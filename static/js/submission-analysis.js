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

		if (tasks.indexOf('build_parse_tree') !== -1 || tasks.indexOf('align_sentence') !== -1) {
			ag.push({
				"user": user,
				"submissions": submissions
			});
		}
		else {
			trad.push({
				"user": user,
				"submissions": submissions
			});
		}
	});

	var counts = [];
	for (var i = 0, u; u = ag[i]; i++) {
		u.slides = this.sortIntoSlides(u.submissions);
		counts = counts.concat(u.slides);
	}

	window.postSlides = ag;
	window.counts = counts;

};

parse.prototype.sortIntoSlides = function(submissions) {
	var completed = [];

	for (var i = 0, s; s = submissions[i]; i++) {

		var slide = 0;

		// Test cases
		//if (s.response.indexOf('"value":"The"') !== -1 || s.response.indexOf('"value":"γὰρ"') !== -1 || s.response.indexOf('"value":"οἵ"') !== -1 || s.response.indexOf('"value":"ἦλθον"') !== -1)
		//	slide = 'ambiguous'
		if (s.response.indexOf('"value":"apple"') !== -1 || s.response.indexOf('"value":"an"') !== -1 || s.response.indexOf('"value":"eats"') !== -1 || s.response.indexOf('"value":"man"') !== -1) 
			slide = '1 - 01'
		else if (s.response.indexOf('"value":"men"') !== -1 || s.response.indexOf('"value":"gods"') !== -1 || s.response.indexOf('"value":"all"') !== -1 || s.response.indexOf('"value":"watch"') !== -1)
			slide = '1 - 02'
		else if (s.response.indexOf('"value":"τρόπῳ"') !== -1 && s.response.indexOf('"id":4') !== -1)
			slide = '1 - 03'
		else if (s.response.indexOf('"value":"Ἀθηναῖοι"') !== -1 && s.response.indexOf('"id":3') !== -1)
			slide = '1 - 03'
		else if (s.response.indexOf('"value":"οἱ"') !== -1 && s.response.indexOf('"id":1') !== -1 && s.response.indexOf('"relation":"Atr"') !== -1)
			slide = '1 - 03'
		else if (s.response.indexOf('"value":"τοιῷδε"') !== -1)
			slide = '1 - 03'
		else if (s.response.indexOf('"value":"ἐπ\'"') !== -1 && s.response.indexOf('"id":39') !== -1) 
			slide = '1 - 04'
		else if (s.response.indexOf('"value":"οἴκου"') !== -1 && s.response.indexOf('"id":40') !== -1) 
			slide = '1 - 04'
		else if (s.response.indexOf('"value":"βασιλεὺς"') !== -1 || s.response.indexOf('"value":"Λεωτυχίδης"') !== -1 || s.response.indexOf('"value":"ἀπεχώρησεν"') !== -1)
			slide = '1 - 04'
		else if (s.response.indexOf('"value":"βραχέα"') !== -1 || s.response.indexOf('"value":"περιβόλου"') !== -1 || s.response.indexOf('"value":"τοῦ"') !== -1 || s.response.indexOf('"value":"εἱστήκει"') !== -1)
			slide = '1 - 09'
		else if (s.response.indexOf('"value":"πρεσβείᾳ"') !== -1 || s.response.indexOf('"value":"δὲ"') !== -1) 
			slide = '1 - 10'
		else if (s.response.indexOf('"value":"Λακεδαιμόνιοι"') !== -1 && s.response.indexOf('"id":1') !== -1) 
			slide = '1 - 10'
		else if (s.response.indexOf('"value":"ἀρχάς"') !== -1 || s.response.indexOf('"value":"οὐ"') !== -1 || s.response.indexOf('"value":"πρὸς"') !== -1 || s.response.indexOf('"value":"τὰς"') !== -1 || s.response.indexOf('"value":"προσῄει"') !== -1)
			slide = '1 - 13'
		else if (s.response.indexOf('"value":"Θεμιστοκλεῖ"') !== -1 || s.response.indexOf('"value":"φιλίαν"') !== -1 || s.response.indexOf('"value":"διὰ"') !== -1 || s.response.indexOf('"value":"αὐτοῦ"') !== -1 || s.response.indexOf('"value":"ἐπείθοντο"') !== -1)
			slide = '1 - 14'
		else if (s.response.indexOf('"value":"τῷ"') !== -1 && s.response.indexOf('"id":4') !== -1)
			slide = '1 - 14'
		else if (s.response.indexOf('"value":"Ἀθηναῖοι"') !== -1 && s.response.indexOf('"id":4') !== -1)
			slide = '1 - 17'
		else if (s.response.indexOf('"value":"πρέσβεις"') !== -1 && s.response.indexOf('"id":6') !== -1)
			slide = '1 - 17'
		else if (s.response.indexOf('"value":"τοὺς"') !== -1) 
			slide = '1 - 17'
		else if (s.response.indexOf('"value":"φανερὰν"') !== -1 || s.response.indexOf('"value":"ὀργὴν"') !== -1 || s.response.indexOf('"value":"Ἀθηναίοις"') !== -1 || s.response.indexOf('"value":"οὐκ"') !== -1 || s.response.indexOf('"value":"τοῖς"') !== -1)
			slide = '1 - 19'
		else if (s.response.indexOf('"value":"ἐπ\'"') !== -1 && s.response.indexOf('"id":6') !== -1)
			slide = '1 - 21'
		else if (s.response.indexOf('"value":"οἴκου"') !== -1 && s.response.indexOf('"id":7') !== -1)
			slide = '1 - 21'
		else if (s.response.indexOf('"value":"πρέσβεις"') !== -1 && s.response.indexOf('"id":3') !== -1)
			slide = '1 - 21'
		else if (s.response.indexOf('"value":"ἑκατέρων"') !== -1 || s.response.indexOf('"value":"ἀνεπικλήτως"') !== -1 || s.response.indexOf('"value":"ἀπῆλθον"') !== -1)
			slide = '1 - 21'
		else if (s.response.indexOf('"value":"Ἀθηναῖοι"') !== -1 && s.response.indexOf('"id":5') !== -1)
			slide = '1 - 22'
		else if (s.response.indexOf('"value":"ἐν"') !== -1 && s.response.indexOf('"id":9') !== -1)
			slide = '1 - 22'
		else if (s.response.indexOf('"value":"τούτῳ"') !== -1 && s.response.indexOf('"id":1') !== -1)
			slide = '1 - 22'
		else if (s.response.indexOf('"value":"τρόπῳ"') !== -1 && s.response.indexOf('"id":3') !== -1)
			slide = '1 - 22'
		else if (s.response.indexOf('"value":"οἱ"') !== -1 && s.response.indexOf('"id":4') !== -1)
			slide = '1 - 22'
		else if (s.response.indexOf('"value":"τῷ"') !== -1 && s.response.indexOf('"id":2') !== -1)
			slide = '1 - 22'
		else if (s.response.indexOf('"value":"πόλιν"') !== -1 || s.response.indexOf('"value":"τὴν"') !== -1 || s.response.indexOf('"value":"χρόνῳ"') !== -1 || s.response.indexOf('"value":"ὀλίγῳ"') !== -1)
			slide = '1 - 22'
		else if (s.response.indexOf('"value":"μάλιστα"') !== -1 || s.response.indexOf('"value":"προσέκειτο"') !== -1)
			slide = '1 - 23'
		else if (s.response.indexOf('"value":"ταῖς"') !== -1 || s.response.indexOf('"value":"ναυσὶ"') !== -1)
			slide = '1 - 25'
		else if (s.response.indexOf('"value":"τούτῳ"') !== -1 && s.response.indexOf('"id":2') !== -1)
			slide = '1 - 27'
		else if (s.response.indexOf('"value":"ἐν"') !== -1 && s.response.indexOf('"id":1') !== -1)
			slide = '1 - 27'
		else if (s.response.indexOf('"value":"Λακεδαιμόνιοι"') !== -1 && s.response.indexOf('"id":5') !== -1)
			slide = '1 - 27'
		else if (s.response.indexOf('"value":"Παυσανίαν"') !== -1 || s.response.indexOf('"value":"μετεπέμποντο"') !== -1)
			slide = '1 - 27'
		else if (s.encounteredWords) {
			s.encounteredWords.forEach(function(CTS) {
				if (CTS.indexOf('urn:cts:greekLit:tlg0003.tlg001.perseus-grc:1.89.1:') !== -1) {
					slide = '1 - 05';
				}
				else if (CTS.indexOf('urn:cts:greekLit:tlg0003.tlg001.perseus-grc:1.90.3:') !== -1) {
					slide = '1 - 06'; 
				}
				else if (CTS.indexOf('urn:cts:greekLit:tlg0003.tlg001.perseus-grc:1.102.1:') !== -1) {
					slide = '1 - 07';
				}
				else if (CTS.indexOf('urn:cts:greekLit:tlg0003.tlg001.perseus-grc:1.105.9:') !== -1) {
					slide = '1 - 08';
				}
				else if (CTS.indexOf('urn:cts:greekLit:tlg0003.tlg001.perseus-grc:1.103.5:') !== -1) {
					slide = '1 - 11';
				}
				else if (CTS.indexOf('urn:cts:greekLit:tlg0003.tlg001.perseus-grc:1.91.8:') !== -1) {
					slide = '1 - 12';
				}
				else if (CTS.indexOf('urn:cts:greekLit:tlg0003.tlg001.perseus-grc:1.93.1:') !== -1) {
					slide = '1 - 15';
				}
				else if (CTS.indexOf('urn:cts:greekLit:tlg0003.tlg001.perseus-grc:1.103.6:') !== -1) {
					slide = '1 - 16';
				}
				else if (CTS.indexOf('urn:cts:greekLit:tlg0003.tlg001.perseus-grc:1.104.1:') !== -1) {
					slide = '1 - 18';
				}
				else if (CTS.indexOf('urn:cts:greekLit:tlg0003.tlg001.perseus-grc:1.93.13:') !== -1) {
					slide = '1 - 20';
				}
				else if (CTS.indexOf('urn:cts:greekLit:tlg0003.tlg001.perseus-grc:1.94.1:') !== -1) {
					slide = '1 - 23';
				}
				else if (CTS.indexOf('urn:cts:greekLit:tlg0003.tlg001.perseus-grc:1.95.3:') !== -1) {
					slide = '1 - 24';
				}
				else if (CTS.indexOf('urn:cts:greekLit:tlg0003.tlg001.perseus-grc:1.105.1:') !== -1) {
					slide = '1 - 26';
				}
			});
		}

		if (slide !== 0 && (s.task === "build_parse_tree" || s.task === "align_sentence")) {
			completed.push(slide);
		}
	}

	console.log(_.uniq(completed).sort());
	return _.uniq(completed).sort();

};

new parse();
