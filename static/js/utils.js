define(['jquery', 'underscore', 'backbone', 'text!smyth.json', 'text!emily_content.json'], function($, _, Backbone, Smyth, Content) {
	var Utils = {};
	Utils.Smyth = JSON.parse(Smyth);
	Utils.Content = JSON.parse(Content);

	return Utils;
});
