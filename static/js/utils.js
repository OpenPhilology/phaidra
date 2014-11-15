// Here is where we will localize the textbook content (i.e. loading de_content.json)

define(['text!/templates/js/display_notification.html'], function(NotificationTemplate) {

	var Utils = {};

	Utils.displayNotification = function(title, message, options) {
		options = options || {};
		var state = options.state || 'ok';
		var el = $('#notification-modal');
		var template = _.template(NotificationTemplate);
		el.html(template({
			title: title,
			message: message,
			state: options.state,
			options: options
		}));

		el.modal().show();
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
			// Genders
			'fem': gettext('Feminine'),
			'neut': gettext('Neuter'),
			'masc': gettext('Masculine'),

			// Number
			'sg': gettext('Singular'),
			'pl': gettext('Plural'),

			// Case
			'nom': gettext('Nominative'),
			'gen': gettext('Genitive'),
			'dat': gettext('Dative'),
			'acc': gettext('Accusative'),

			// Person
			'3rd': gettext('3rd Person'),
			'2nd': gettext('2nd Person'),
			'1st': gettext('1st Person'),

			// Mood
			'ind': gettext('Indicative'),
			'subj': gettext('Subjunctive'),
			'opt': gettext('Optative'),
			'inf': gettext('Infinitive'),

			// Tense
			'aor': gettext('Aorist'),
			'imperf': gettext('Imperfect'),
			'fut': gettext('Future'),
			'pres': gettext('Present'),
			'futperf': gettext('Future Perfect'),

			// Voice
			'act': gettext('Active'),
			'mid': gettext('Middle'),
			'mp': gettext('Middle/Passive'),
			'pass': gettext('Passive')
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

	Utils.lDistance = function(s, t) {
		if (s.length === 0)
			return t.length;
		if (t.length === 0)
			return s.length;

		var that = this;

		return Math.min(
			that.lDistance(s.substr(1), t) + 1,
			that.lDistance(t.substr(1), s) + 1,
			that.lDistance(s.substr(1), t.substr(1)) + (s[0] !== t[0] ? 1 : 0)
		);
	};

	Utils.compareStrings = function(a, b) {
		var lengthA = a.length;
		var lengthB = b.length;
		var equiv = 0;
		var minLength = (a.length > b.length) ? b.length : a.length;
		var maxLength = (a.length < b.length) ? b.length : a.length;

		for (var i = 0; i < minLength; i++) {
			if (a[i] == b[i])
				equiv++;
		}

		var weight = equiv / maxLength;

		return weight * 100;
	};

	Utils.removeDiacritics = function(text) {
		text = text.replace(/Ά|Α|ά|ἀ|ἁ|ἂ|ἃ|ἄ|ἅ|ἆ|ἇ|ὰ|ά|ᾀ|ᾁ|ᾂ|ᾃ|ᾄ|ᾅ|ᾆ|ᾇ|ᾰ|ᾱ|ᾲ|ᾳ|ᾴ|ᾶ|ᾷ|Ἀ|Ἁ|Ἂ|Ἃ|Ἄ|Ἅ|Ἆ|Ἇ|ᾈ|ᾉ|ᾊ|ᾋ|ᾌ|ᾍ|ᾎ|ᾏ|Ᾰ|Ᾱ|Ὰ|Ά|ᾼ/g,'α');
		text = text.replace(/Έ|Ε|έ|ἐ|ἑ|ἒ|ἓ|ἔ|ἕ|ὲ|έ|Ἐ|Ἑ|Ἒ|Ἓ|Ἔ|Ἕ|Ὲ|Έ/g,'ε');
		text = text.replace(/Ή|Η|ή|ἠ|ἡ|ἢ|ἣ|ἤ|ἥ|ἦ|ἧ|ὴ|ή|ᾐ|ᾑ|ᾒ|ᾓ|ᾔ|ᾕ|ᾖ|ᾗ|ῂ|ῃ|ῄ|ῆ|ῇ|Ἠ|Ἡ|Ἢ|Ἣ|Ἤ|Ἥ|Ἦ|Ἧ|ᾘ|ᾙ|ᾚ|ᾛ|ᾜ|ᾝ|ᾞ|ᾟ|Ὴ|Ή|ῌ/g,'η');
		text = text.replace(/Ί|Ϊ|Ι|ί|ΐ|ἰ|ἱ|ἲ|ἳ|ἴ|ἵ|ἶ|ἷ|ὶ|ί|ῐ|ῑ|ῒ|ΐ|ῖ|ῗ|Ἰ|Ἱ|Ἲ|Ἳ|Ἴ|Ἵ|Ἶ|Ἷ|Ῐ|Ῑ|Ὶ|Ί/g,'ι');
		text = text.replace(/Ό|Ο|ό|ὀ|ὁ|ὂ|ὃ|ὄ|ὅ|ὸ|ό|Ὀ|Ὁ|Ὂ|Ὃ|Ὄ|Ὅ|Ὸ|Ό/g,'ο');
		text = text.replace(/Ύ|Ϋ|Υ|ΰ|ϋ|ύ|ὐ|ὑ|ὒ|ὓ|ὔ|ὕ|ὖ|ὗ|ὺ|ύ|ῠ|ῡ|ῢ|ΰ|ῦ|ῧ|Ὑ|Ὓ|Ὕ|Ὗ|Ῠ|Ῡ|Ὺ|Ύ/g,'υ');
		text = text.replace(/Ώ|Ω|ώ|ὠ|ὡ|ὢ|ὣ|ὤ|ὥ|ὦ|ὧ|ὼ|ώ|ᾠ|ᾡ|ᾢ|ᾣ|ᾤ|ᾥ|ᾦ|ᾧ|ῲ|ῳ|ῴ|ῶ|ῷ|Ὠ|Ὡ|Ὢ|Ὣ|Ὤ|Ὥ|Ὦ|Ὧ|ᾨ|ᾩ|ᾪ|ᾫ|ᾬ|ᾭ|ᾮ|ᾯ|Ὼ|Ώ|ῼ/g,'ω');
		text = text.replace(/ῤ|ῥ|Ῥ/g,'ρ');
		text = text.replace(/Σ|ς/g,'σ');

		return text;
	}

	// Nothing about this is good, but...it was tedious
	Utils.romanize = function(text) {
		text = text.replace(/Ἆ|Ἇ|Ᾱ/g,'Ā');
		text = text.replace(/Ά|Α|Ἀ|Ἁ|Ἂ|Ἃ|Ἄ|Ἅ|Ἆ|Ἇ|Ὰ|Ά/g,'A');
		text = text.replace(/ᾎ|ᾏ/g,'Āi');
		text = text.replace(/ᾈ|ᾉ|ᾊ|ᾋ|ᾌ|ᾍ|ᾼ/g,'Ai');
		text = text.replace(/α|ά|ἀ|ἁ|ἂ|ἃ|ἄ|ἅ|ὰ|ά|ᾰ/g,'a');
		text = text.replace(/ἆ|ἇ|ᾱ|ᾶ/g,'ā');
		text = text.replace(/ᾆ|ᾇ|ᾷ/g,'āi');
		text = text.replace(/ᾀ|ᾁ|ᾂ|ᾃ|ᾄ|ᾅ|ᾷ/g,'ai');

		text = text.replace(/Β/g,'B');
		text = text.replace(/β/g,'b');

		text = text.replace(/Γ/g,'G');
		text = text.replace(/γ/g,'g');

		text = text.replace(/Δ/g,'D');
		text = text.replace(/δ/g,'d');

		text = text.replace(/Μ/g,'M');
		text = text.replace(/μ/g,'m');

		text = text.replace(/Χ/g,'X');
		text = text.replace(/χ/g,'x');

		text = text.replace(/Κ/g,'K');
		text = text.replace(/κ/g,'k');

		text = text.replace(/Ν/g,'N');
		text = text.replace(/ν/g,'n');

		text = text.replace(/Ζ/g,'Z');
		text = text.replace(/ζ/g,'z');

		text = text.replace(/Ξ/g,'Ks');
		text = text.replace(/ξ/g,'ks');

		text = text.replace(/Λ/g,'L');
		text = text.replace(/λ/g,'l');

		text = text.replace(/Π/g,'P');
		text = text.replace(/π/g,'p');

		text = text.replace(/Τ/g,'T');
		text = text.replace(/τ/g,'t');

		text = text.replace(/Θ/g,'Th');
		text = text.replace(/θ/g,'th');

		text = text.replace(/Φ/g,'Ph');
		text = text.replace(/φ/g,'ph');

		text = text.replace(/Ή|Η|Ἠ|Ἡ|Ἢ|Ἣ|Ἤ|Ἥ|Ἦ|Ἧ|Ή/g,'Ē');
		text = text.replace(/ᾘ|ᾙ|ᾚ|ᾛ|ᾜ|ᾝ|ᾞ|ᾟ|ῌ/g,'Ēi');
		text = text.replace(/ή|ἠ|ἡ|ἢ|ἣ|ἤ|ἥ|ἦ|ἧ|η|ὴ|ή|ῆ/g,'ē');
		text = text.replace(/ᾐ|ᾑ|ᾒ|ᾓ|ᾔ|ᾕ|ᾖ|ᾗ|ῂ|ῃ|ῄ|ῇ/g,'ēi');

		text = text.replace(/Έ|Ε|Ἐ|Ἑ|Ἒ|Ἓ|Ἔ|Ἕ|Ὲ|Έ/g,'E');
		text = text.replace(/έ|ἐ|ἑ|ἒ|ἓ|ἔ|ἕ|ὲ|έ|ε/g,'e');

		text = text.replace(/Ί|Ϊ|Ι|Ἰ|Ἱ|Ἲ|Ἳ|Ἴ|Ἵ|Ἶ|Ἷ|Ῐ|Ῑ|Ὶ|Ί/g,'I');
		text = text.replace(/Ί|Ϊ|Ι|ί|ΐ|ἰ|ἱ|ἲ|ἳ|ἴ|ἵ|ἶ|ἷ|ι|ὶ|ί|ῐ|ῑ|ῒ|ΐ|ῖ|ῗ|Ἰ|Ἱ|Ἲ|Ἳ|Ἴ|Ἵ|Ἶ|Ἷ|Ῐ|Ῑ|Ὶ|Ί/g,'i');

		text = text.replace(/Ό|Ο|Ὀ|Ὁ|Ὂ|Ὃ|Ὄ|Ὅ|Ὸ|Ό/g,'O');
		text = text.replace(/ό|ὀ|ὁ|ὂ|ὃ|ὄ|ὅ|ὸ|ό/g,'o');

		text = text.replace(/Ύ|Ϋ|Υ|Ὑ|Ὓ|Ὕ|Ὗ|Ῠ|Ῡ|Ὺ|Ύ/g,'U');
		text = text.replace(/ΰ|ϋ|ύ|ὐ|ὑ|ὒ|ὓ|ὔ|ὕ|ὖ|ὗ|ὺ|ύ|ῠ|ῡ|ῢ|ΰ|ῦ|ῧ/g,'u');

		text = text.replace(/Ώ|Ω|Ὠ|Ὡ|Ὢ|Ὣ|Ὤ|Ὥ|Ὦ|Ὧ|Ὼ|Ώ/g,'Ō');
		text = text.replace(/ᾨ|ᾩ|ᾪ|ᾫ|ᾬ|ᾭ|ᾮ|ᾯ|ῼ/g,'Ōi');
		text = text.replace(/ώ|ὠ|ὡ|ὢ|ὣ|ὤ|ὥ|ὦ|ὧ|ὼ|ώ|ῶ|ω/g,'ō');
		text = text.replace(/ᾠ|ᾡ|ᾢ|ᾣ|ᾤ|ᾥ|ᾦ|ᾧ|ῲ|ῳ|ῴ|ῷ/g,'ōi');

		text = text.replace(/Ῥ/g,'R');
		text = text.replace(/ρ|ῤ|ῥ/g,'r');

		text = text.replace(/Σ/g,'S');
		text = text.replace(/ς|σ/g,'s');

		return text;
	};

	return Utils;
});
