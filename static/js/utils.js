define(['jquery', 'underscore', 'text!json/smyth.json', 'text!json/en_content.json'], function($, _, Smyth, Content) {
	var Utils = {};
	Utils.Smyth = JSON.parse(Smyth);

	// Here is where we will localize the textbook content
	Utils.Content = JSON.parse(Content);

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

	return Utils;
});
