define(['jquery', 
	'underscore', 
	'backbone', 
	'utils'], 
	function($, _, Backbone, Utils) {

		return Backbone.Model.extend({
			/**
			 * Word Model
			 * @constructs
			 * @augments external:Backbone.Model
			 */ 
			defaults: {
				'modelName': 'word',
				'selected': false
			},
			idAttribute: 'CTS',
			initialize: function(attributes) {
				if (!attributes.CTS && attributes.sentenceCTS)
					this.set('CTS', attributes.sentenceCTS + ':' + (attributes.index + 1));
			},
			url: function() {
				return this.get('resource_uri');
			},
			parse: function(response) {
				this.set(response);
			},
			equiv: function(other) {
				return this.get('CTS') === other.CTS;
			},			
			getDefinition: function(target_lang) {
				if (!this.get('translations') || this.get('translations').length === 0)
					return false;
				
				var words = this.get('translations').filter(function(word) {
					return word.lang === target_lang;
				});

				var definition = words.reduce(function(memo, word) {
					memo += word.value + ' ';
					return memo;
				}, '').trim();

				return definition;
			},
			getHumanReadableMorph: function() {
				var attrs = [];
				switch (this.get('pos')) {
					case 'verb':
						attrs.push(Utils.getHumanReadableMorph(this.get('person')), 
							Utils.getHumanReadableMorph(this.get('number')), 
							Utils.getHumanReadableMorph(this.get('tense')),
							Utils.getHumanReadableMorph(this.get('voice')),
							Utils.getHumanReadableMorph(this.get('mood')));
						break;
					default:
						attrs.push(Utils.getHumanReadableMorph(this.get('case')), 
							Utils.getHumanReadableMorph(this.get('number')), 
							Utils.getHumanReadableMorph(this.get('gender')));
						break;
				}

				return _.compact(attrs).join(', ');
			}
		});
	}
);
