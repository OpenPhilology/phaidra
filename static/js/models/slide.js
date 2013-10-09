/*

Slide: Lowest level component in learning hierarchy.

*/
Phaidra.Models.Slide = Phaidra.Models.Base.extend({
	defaults: {
		'modelName': 'slide',
		'uid': 0,
		'title': '',
		'content': '',
		'options': ['a', 'b', 'c'],
		'submission': ''
	},
	// Check user's submission against the server 
	checkSubmission: function(submission, options) {
		var that = this;

		this.save({ 
				submission: submission 
			},
			{ 
				patch: true,

				// Allow views to handle how passing and failing submissions are handled
				success: function(model, response, options) {
					if (that.options && that.options.success)
						that.options.success(model, response, options);					
				},
				error: function(model, xhr, options) {
					if (that.options && that.options.error)
						that.options.error(model, xhr, options);
				}
			}
		);
	}
});
_.extend(Phaidra.Models.Slide.defaults, Phaidra.Models.Base.defaults);
