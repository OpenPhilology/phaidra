/*

Module: A module is a collection of slides, plus other specific data that is derived from a user's progress.

*/
Phaidra.Models.Module = Phaidra.Models.Base.extend({
	defaults: {
		'modelName': 'module',
		'title': '',
		'slides': {},
		'levels': 1
	}
});

_.extend(Phaidra.Models.Module.defaults, Phaidra.Models.Base.defaults);

