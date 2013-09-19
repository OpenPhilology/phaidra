Phaidra.Models.Base = Backbone.Model.extend({
	defaults: {
		'modelName': 'base'
		'urlRoot': '/api/'
	},
	url: function() {
		return this.urlRoot + this.modelName;		
	},
});
