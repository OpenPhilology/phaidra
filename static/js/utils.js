define(['jquery', 'underscore', 'text!json/smyth.json', 'text!json/emily_content.json'], function($, _, Smyth, Content) {
	var Utils = {};
	Utils.Smyth = JSON.parse(Smyth);
	Utils.Content = JSON.parse(Content);

	Utils.getDefiniteArticle = function(gender) {
		var map = {
			'masc': 'ὁ',
			'fem': 'ἡ',
			'neut': 'τό'
		};

		return map[gender];
	};

	Utils.getHelpTopics = function(smyth) {
		// Get links to relevant content from Utils.Content based on smyth in the exercise
	};

	Utils.makeHint = function(smyth, mistake) {
		// Use smyth ref and mistake made to give reasonable hints	
	};

	return Utils;
});
