from django.contrib import admin
from app.models import Language, Category, AppUser, Grammar, Content  
from django import forms
from django.db import models

class LargeTextarea(forms.Textarea):
	def __init__(self, *args, **kwargs):
		attrs = kwargs.setdefault('attrs', {})
		attrs.setdefault('style', 'width: 80%; height: 500px')
		super(LargeTextarea, self).__init__(*args, **kwargs)

class LargeTextInput(forms.TextInput):
	def __init__(self, *args, **kwargs):
		attrs = kwargs.setdefault('attrs', {})
		attrs.setdefault('style', 'width: 80%')
		super(LargeTextInput, self).__init__(*args, **kwargs)

class LargeSelectMultiple(forms.SelectMultiple):
	def __init__(self, *args, **kwargs):
		attrs = kwargs.setdefault('attrs', {})
		attrs.setdefault('style', 'width: 80%')
		super(LargeSelectMultiple, self).__init__(*args, **kwargs)

class GrammarAdmin(admin.ModelAdmin):
	list_filter = ('title', 'ref', 'query', 'category')
	list_display = ['title', 'ref', 'query', 'category']
	formfield_overrides = {
		models.CharField: { 'widget': LargeTextInput },
		models.TextField: { 'widget': LargeTextarea },
		# models.MultipleChoiceField: { 'widget': LargeSelectMultiple }
	}

class ContentAdmin(admin.ModelAdmin):
	list_filter = ('title', 'grammar_ref')
	list_display = ['title', 'grammar_ref', 'source_lang', 'target_lang', 'related_topics']
	filter_vertical = ('related_topics',)
	list_display_links = ('title',)

	formfield_overrides = {
		models.CharField: { 'widget': LargeTextInput },
		models.TextField: { 'widget': LargeTextarea },
		# models.MultipleChoiceField: { 'widget': LargeSelectMultiple }
	}

admin.site.register(AppUser)
admin.site.register(Language)
admin.site.register(Category)
admin.site.register(Grammar, GrammarAdmin)
admin.site.register(Content, ContentAdmin)

