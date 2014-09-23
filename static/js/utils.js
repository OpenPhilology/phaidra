// Here is where we will localize the textbook content (i.e. loading de_content.json)

define(['jquery', 'underscore', 'text!json/smyth.json', 'text!json/en_content.json', 'text!json/en_question_bank.json', 'text!json/en_tasks.json'], function($, _, Smyth, Content, Questions, Tasks) {
	var Utils = {};
	Utils.Smyth = JSON.parse(Smyth)[0];

	Utils.Content = JSON.parse(Content);
	Utils.Questions = JSON.parse(Questions);
	Utils.Tasks = JSON.parse(Tasks);

	Utils.getDefiniteArticle = function(gender) {
		var map = {
			'masc': 'ὁ',
			'fem': 'ἡ',
			'neut': 'τό'
		};

		return map[gender];
	};

	Utils.getHTMLbySmyth = function(smyth) {
		// Get the HTML links that match a Smyth unit
		var urls = [];
		
		for (var i = 0; i < Utils.Content.length; i++) {
			if (Utils.Content[i]["modules"]) {
				for (var j = 0; j < Utils.Content[i]["modules"].length; j++) {
					var slides = Utils.Content[i]["modules"][j]["slides"];
					for (var k = 0; k < slides.length; k++) {
						if (slides[k]["smyth"] == smyth)
							urls.push(slides[k]["includeHTML"]);
					}
				}
			}
		}

		return urls;
	};
	
	var persian = { 0: '۰', 1: '۱', 2: '۲', 3: '۳', 4:'۴', 5:'۵', 6: '۶', 7: '۷', 8: '۸', 9: '۹'};

	Utils.convertToPersian = function(text) {
		for (var i = 0; i < 10; i++) {
			text = text.replace(eval('/' + i + '/g'), persian[i]);
		}
		return text;
	};

	Utils.getHelpTopics = function(smyth) {
		// Get links to relevant content from Utils.Content based on smyth in the exercise
	};

	Utils.makeHint = function(smyth, mistake) {
		// Use smyth ref and mistake made to give reasonable hints	
	};
	Utils.getReadableLang = function(abbreviation) {
		var langs = {
			'grc': gettext('Ancient Greek'),
			'fa': gettext('Farsi'),
			'en': gettext('English'),
			'hr': gettext('Croatian'), 
			'pr': gettext('Portuguese'),
			'fr': gettext('French')
		};

		return langs[abbreviation];
	};

	Utils.fireEvent = function(el, type) {
		if (el.fireEvent) {
			el.fireEvent('on' + type);
		}
		else {
			var e = document.createEvent('Events');
			e.initEvent(type, true, false);
			el.dispatchEvent(e);
		}
	};

	Utils.parseCTS = function(CTS) {
		/*	CTS example:	urn:	cts:	greekLit:	tlg0003.tlg001.perseus-grc:		1.89.1:		13
							urn:	cts:	namespace:	work:							passage:	word
		*/ 
		var split = CTS.split(":");
		var work = split[3].split(".");

		var obj = {
			"urn": split[0],
			"cts": split[1],
			"namespace": split[2],
			"work": {
				"textgroup": work[0],
				"text": work[1],
				"translation": work[2]
			},
			"sentence": split[4]
		};

		if (split.length === 6)
			obj["word"] = split[5];

		return obj;
	};

	return Utils;
});
