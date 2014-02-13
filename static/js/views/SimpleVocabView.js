define(['jquery', 'underscore', 'backbone', 'models', 'collections'], function($, _, Backbone, Models, Collections) {
	var View = Backbone.View.extend({
		tagName: 'div',
		className: 'slide-unit',
		events: {
			"click .word a" : "toggleAnswer"
			},
		initialize: function(options) {
		       this.$el.html(options.template(this.model.attributes));
			this.loadImage(this.model.attributes['image'])

		},
		render: function() {
   
			return this;	
		},
		renderImagePart:function(visible)
		{

		
		if (visible==true)
		{

				 this.$el.find('.vocab_image_container').toggle(visible).css({'background-image':"url("+this.model.attributes.image+")"})
		if (this.model.attributes.hide_options_on_image_exists==true)
		 this.$el.find('.sentence').hide()

		}		
		}
		,
		loadImage:function(filename){
		var self=this;
		if (!filename) return;
		var img = $("<img />").attr('src', filename)
		    .load(function() {
			if (!this.complete || typeof this.naturalWidth == "undefined" || this.naturalWidth == 0) {
			  self.renderImagePart(false)
			} else {
				
				self.renderImagePart(true)
			}
		    });		
		},
		toggleAnswer:function(e)
		{
		var theWord = $(e.target).parent();
		theWord.toggleClass("word-selected")
	        
                this.translate(theWord.text(),theWord)
		
		//prepare values for validation
				var attempt = [];
				var selectedWords = this.$el.find('.word-selected');
				for (var i = 0; i < selectedWords.length; i++)
					attempt.push($(selectedWords[i]).text())

				this.checkAnswer(attempt);
			       

		
		},
		translate:function(word,target){
		if (typeof word =='string')
		$.ajax({  
		    url: 'https://ajax.googleapis.com/ajax/services/language/translate',  
		    dataType: 'jsonp',
		    data: { q: word,  // text to translate
			    v: '1.0',
			    langpair: 'en|el' },   // '|es' for auto-detect
		    success: function(result) {
			target.attr('title',result.responseData.translatedText);
		    },  
		    error: function(XMLHttpRequest, errorMsg, errorThrown) {
			console.log(errorMsg);
			target.attr('title',"no translation found");
		    }  
		});
		},
		checkAnswer: function(attempt) {

			if (this.model.checkAnswer(attempt)) {

				// Display correct answer message
				var info = this.$el.find('.alert');
				info.html(this.model.get('successMsg'));
				info.removeClass('alert-info');
				info.addClass('alert-success');
				info.slideDown();
			}
			else {

				// Give the user a hint so they can try again
				var info = this.$el.find('.alert');
				info.html(this.model.get('hintMsg'));
				info.removeClass('alert-success');
				info.addClass('alert-info');
				info.slideDown();
			}
		}
	});

	return View;
});
