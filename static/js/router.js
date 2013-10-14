$(function() {
	$('.sec').tooltip();
	$('.module .circle').tooltip({ container: 'body'});

	var slides = new Phaidra.Collections.Slides([
		{
			title: 'Feminines in -&eta;',
			content: 'What is the nominative singular form for "The Fine Tent"?',
			type: 'slide_multi_composition',
			options: [
				[{
					display: 'ἡ',
					value: 'ἡ'
				},
				{
					display: 'τῆς',
					value: 'τῆς`'
				}],
				[{
					display: 'καλαῖς',
					value: 'καλαῖς'
				},
				{
					display: 'καλὴ',
					value: 'καλὴ'
				}],
				[{
					display: 'σκηνῆς',
					value: 'σκηνῆς'
				},
				{
					display: 'σκηνή',
					value: 'σκηνή'
				}]
			]
		},
		{
			title: 'Other',
			content: 'second content',
			type: 'slide_multi_composition',
			options: [
				[{
					display: 'choice',
					value: 'choice'
				}]
			]
		}
	]);

	// Test objects
	Phaidra.TestModule = new Phaidra.Models.Module({
		title: 'Alpha Nouns', 
		slides: slides,
	});

	new Phaidra.Views.Module({ el: '.slide', model: Phaidra.TestModule }).render();

});
