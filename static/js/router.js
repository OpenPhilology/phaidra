/*$(function() {
	new Phaidra.Views.ProgressViz({el: '.work'}).render();
});*/

$(function() {
	$('.sec').tooltip();
	$('.module .circle').tooltip({ container: 'body'});

	console.log(Phaidra.Collections);
	console.log(typeof(Phaidra.Collections.Slides));

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
		}
	]);

	// Test objects
	Phaidra.TestModule = new Phaidra.Models.Module([
		{
			title: 'Alpha Nouns', 
			slides: slides,
		}
	]);

	new Phaidra.Views.MultiCompositionSlide({ el: '.multi-slide', model: Phaidra.TestModule }).render();
});
