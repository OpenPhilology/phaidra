define(['jquery', 'underscore', 'backbone', 'models', 'text!emily_content.json'], function($, _, Backbone, Models, Content) {

	var Collections = {};

	// Some modifications to Backbone to work with Tastypie
	Collections.Base = Backbone.Collection.extend({
		urlRoot: '/api/',
		url: function() {
			return this.urlRoot + '/' + this.model.prototype.defaults.modelName + '/';		
		},
		parse: function(response) {
			// Since Tastypie gives us metadata about our objects, store that on the collection
			// and assign the actual objects to the collection itself.

			if (response && response.meta)
				this.meta = response.meta;

			return (response && response.objects ? response.objects : response) || response;
		},
		sync: function(options) {
			// Make sure that CSRF Tokens are sent with every request
			// GetCookie function from: https://docs.djangoproject.com/en/dev/ref/contrib/csrf/

			var getcookie = function(name) {
				var value = null;
				if (document.cookie && document.cookie != '') {
					var cookies = document.cookie.split(';');
					for (var i = 0; i < cookies.length; i++) {
						var cookie = $.trim(cookies[i]);
						if (cookie.substring(0, name.length + 1) == (name + '=')) {
							value = decodeURIComponent(cookie.substring(name.length + 1));
							break;
						}
					}
				}
				return value;
			}

			options.headers = {
				'X-CSRFToken': getcookie('csrftoken')
			};

			(_.bind(Backbone.Collection.prototype.sync, this, options))();
		}
	});

	Collections.Slides = Backbone.Collection.extend({
		model: Models.Slide,
		initialize: function(models, options) {
			var that = this;

			/* Is this really bad? */
			if (!this._meta)
				this._meta = [];

			this.meta = function(prop, value) {
				if (value == undefined)
					return this._meta[prop];
				else
					this._meta[prop] = value;
			};

			that.meta('module', parseInt(options.module));
			that.meta('section', parseInt(options.section));
		},
		populate: function(collection) {
			var that = this;

			// Get the data we care about -- specific section of a module
			data = JSON.parse(Content);
			var slide_data = data[that.meta('module')]["modules"][that.meta('section')]["slides"];

			/*
			Goes through and creates either an individual slide, or a cluster of slides,
			based on data from the JSON file.
			*/

			// Set attributes on this object
			that.meta('title', data[that.meta('module')]["title"]);

			for (var i = 0; i < slide_data.length; i++) {
				if (slide_data[i]["smyth"] && slide_data[i]["type"] == 'slide_info') {
					// Create data needed for a an exercise
					console.log("Adding an exercise for " + slide_data[i]["smyth"]);
					var new_slide = {
						"smyth": slide_data[i]["smyth"],
						"task": slide_data[i]["tasks"][0]
					};
					/* For now, insert 4.
					slide_data.splice(i, 0, new_slide);
					slide_data.splice(i, 0, new_slide);
					slide_data.splice(i, 0, new_slide);*/
					slide_data.splice(i, 0, new_slide);
					i++;
				}
			}

			that.meta('initLength', slide_data.length);

			// Build with slide data
			for (var i = 0; i < slide_data.length; i++) {
				that.add(new Models.Slide(slide_data[i]));
			}
		}
	});

	Collections.Vocab = Backbone.Collection.extend({
		model: Models.Word
	});

	return Collections;
});
