/*$(function() {
	new Phaidra.Views.ProgressViz({el: '.work'}).render();
});*/

$(function() {
	$('.sec').tooltip();
	$('.module .circle').tooltip({ container: 'body'});

	var testSlide = new Phaidra.Models.Slide({
		options: ['a', 'b', 'c']
	});

	new Phaidra.Views.MultiCompositionSlide({ el: '.multi-slide', model: testSlide}).render();
});
