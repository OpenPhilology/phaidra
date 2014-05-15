define(['jquery', 'underscore', 'backbone', 'models', 'utils'], function($, _, Backbone, Models, Utils) {

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

			// Keep track of metadata about the collection
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
			var slide_data = Utils.Content[that.meta('module')]["modules"][that.meta('section')]["slides"];

			/*
			Goes through and creates either an individual slide, or a cluster of slides,
			based on data from the JSON file.
			*/

			// Set attributes on this object
			that.meta('title', Utils.Content[that.meta('module')]["title"]);

			for (var i = 0; i < slide_data.length; i++) {
				slide_data[i]["title"] = that.meta('title');
				if (slide_data[i]["smyth"] && slide_data[i]["tasks"] && slide_data[i]["type"] == 'slide_info') {
					// Create data needed for a an exercise
					console.log("Adding an exercise for " + slide_data[i]["smyth"]);
					
					var j = Math.floor((Math.random() * slide_data[i]["tasks"].length) + 1);

					slide_data.splice(i+1, 0, {
						"smyth": slide_data[i]["smyth"],
						"task": slide_data[i]["tasks"][j - 1]
					});

					j = Math.floor((Math.random() * slide_data[i]["tasks"].length) + 1);
					slide_data.splice(i+1, 0, {
						"smyth": slide_data[i]["smyth"],
						"task": slide_data[i]["tasks"][j - 1]
					});

					j = Math.floor((Math.random() * slide_data[i]["tasks"].length) + 1);
					slide_data.splice(i+1, 0, {
						"smyth": slide_data[i]["smyth"],
						"task": slide_data[i]["tasks"][j - 1]
					});
					i += 3;
				}
			}

			that.meta('initLength', slide_data.length);

			// Build with slide data
			for (var i = 0; i < slide_data.length; i++) {
				that.add(new Models.Slide(slide_data[i]));
			}
		}
	});

	Collections.Words = Backbone.Collection.extend({
		model: Models.Word,
		initialize: function() {
			if (!this._meta)
				this._meta = [];

			this.meta = function(prop, value) {
				if (value == undefined)
					return this._meta[prop];
				else
					this._meta[prop] = value;
			};
		},
		populate: function(sentenceURI) {
			var that = this;

			// First, make sure this isn't already populated by seeing if lemma attribute is there
			if (!that.findWhere({ sentenceURI: sentenceURI }).get('lemma')) {

				// Populates a subset of the data based on the sentence URI
				$.ajax({
					url: sentenceURI,
					dataType: 'json',
					success: function(response) {
						var words = response.words;

						for (var i = 0; i < words.length; i++) {
							that.findWhere({ CTS : words[i]["CTS"] }).set(words[i]);
						}

						that.trigger('populated');
					},
					error: function(x, y, z) {
						console.log(x, y, z);
					}
				});
			}
			else {
				that.trigger('populated');
			}
		}
	});

	return Collections;
});
