// Here is where we will localize the textbook content (i.e. loading de_content.json)

define(['jquery', 'underscore', 'text!/static/json/smyth.json', 'text!/static/json/en_content.json', 'text!/static/json/en_question_bank.json', 'text!/static/json/en_tasks.json'], function($, _, Smyth, Content, Questions, Tasks) {
	var Utils = {};

	/**
	  * Our static content, used to programmatically generate exercises:
	  */ 
	Utils.Smyth = JSON.parse(Smyth);						// Smyth ref to query mapper
	Utils.Content = JSON.parse(Content);					// Gives us the HTML which corresponds to Smyth, and meta material
	Utils.Questions = JSON.parse(Questions);				// Statically written questions for non-text questions
	Utils.Tasks = JSON.parse(Tasks);						// Templates for programmatically generated text-based questions

	/**
	  * SMYTH HELPER FUNCTIONS
	  * These functions help with referencing all of our components (lesson content, tasks, and questions) back to
	  * the source text data. See static/js/json/smyth.json for a clearer idea.
	  */
	Utils.Slides = (function() {
		return _.flatten(_.pluck(_.flatten(_.pluck(Utils.Content, 'modules')), 'slides'));
	})();
	Utils.Microlessons = (function() {
		var smyths = _.compact(_.pluck(Utils.Slides, 'smyth'));
		return _.uniq(smyths.map(function(s) {
			return s.split('#')[0];
		}));
	})();
	Utils.getSmyth = function(smyth) {
		return Utils.Smyth.filter(function(s) {
			return smyth === s.ref;
		})[0];
	};
	Utils.getRelatedSmyth = function(smyth) {
		var generalSmyth = smyth.split('#')[0]; 

		return Utils.Smyth.filter(function(s) {
			return generalSmyth === s.ref.split('#')[0];
		});
	};
	// Get the lesson that contains the microlesson
	Utils.getLesson = function(smyth) {
		return Utils.Content.filter(function(lesson) {
			var smyths = _.pluck(_.flatten(lesson.modules.map(function(m) {
				return m.slides;
			})), 'smyth');
			return smyths.indexOf(smyth.split('#')[0]) !== -1;
		})[0];
	};
	Utils.getThumbnail = function(smyth) {
		smyth = smyth.split('#')[0];

	};

	Utils.getHTMLbySmyth = function(smyth) {
		// Get the HTML links that match a Smyth unit
		if (!smyth) return [];
		if (typeof(smyth) === "string") smyth = [smyth];
		smyth = _.pluck(smyth, 'key');
		
		var matches = _.flatten(Utils.Content.map(function(unit) {
			return _.pluck(unit.modules, 'slides');
		})).filter(function(slide) { return smyth.indexOf(slide.smyth) !== -1; });

		return matches;
	};

	Utils.removeQueryParam = function(query, toRemove) {
		var parts = query.split('&'), adjusted = '';
		for (var i = 0, part; part = parts[i]; i++) {
			if (part.indexOf(toRemove) !== -1) {
				delete part;
				break;
			}
		}
		return parts.join('&');
	};

	Utils.extractQueryParamValue = function(query, toExtract) {
		var parts = query.split('&'), found = '';
		for (var i = 0, part; part = parts[i]; i++) {
			if (part.indexOf(toExtract) !== -1) {
				found = part.split('=')[1]; 	
				break;
			}
		}
		return found;
	};

	Utils.getHelpTopics = function(smyth) {
		// Get links to relevant content from Utils.Content based on smyth in the exercise
	};

	Utils.makeHint = function(smyth, mistake) {
		// Use smyth ref and mistake made to give reasonable hints	
	};

	
	/**
	 * Functions for working with Persian.
	 */
	var persian = { 0: '۰', 1: '۱', 2: '۲', 3: '۳', 4:'۴', 5:'۵', 6: '۶', 7: '۷', 8: '۸', 9: '۹'};

	Utils.convertToPersian = function(text) {
		for (var i = 0; i < 10; i++) {
			text = text.replace(eval('/' + i + '/g'), persian[i]);
		}
		return text;
	};

	/**
	 * Helper functions for working with Greek.
	 */ 
	Utils.getDefiniteArticle = function(gender, number) {
		number = number || 'sg';
		var map = {
			'sg': {
				'masc': 'ὁ',
				'fem': 'ἡ',
				'neut': 'τό'
			},
			'pl': {
				'masc': 'οἱ',
				'fem': 'αἱ',
				'neut': 'τά'
			}
		};

		return map[number][gender];
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

	Utils.getVocabBlacklist = function(pos, lang) {
		lang = lang || 'en';

		var list = [];
		switch (lang) {
			case 'en':
				if (pos === 'verb')
					list = ['they', 'he', 'she', 'being', 'it', 'was', 'as', 'having', 'been', 'that', 'to', 'them', 'should', 'would', 'who', 'were', 'so', 'by', 'of'];
				else if (pos === 'noun')
					list = ['a', 'the', 'by', 'to', 'for', 'an', 'after', 'in', 'on', 'with']
				break;
			default:
				list = [];
		}

		return [];
	};

	Utils.getHumanReadableMorph = function(str) {
		var map = {
			'fem': gettext('Feminine'),
			'sg': gettext('Singular'),
			'gen': gettext('Genitive'),
			'pl': gettext('Plural'),
			'nom': gettext('Nominative'),
			'aor': gettext('Aorist'),
			'act': gettext('Active'),
			'ind': gettext('Indicative'),
			'3rd': gettext('3rd Person'),
			'2nd': gettext('2nd Person'),
			'1st': gettext('1st Person'),
			'masc': gettext('Masculine'),
			'imperf': gettext('Imperfect'),
			'fut': gettext('Future')
		};
		return map[str] || str;
	};

	/**
	 * General javascript utilities. 
	 */
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


	return Utils;
});
