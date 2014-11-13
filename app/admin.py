from django.contrib import admin
from app.models import Language, Category, AppUser, Grammar, Content, Aspect, Task, TaskSequence, TaskContext
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
        list_filter = ('title', 'query', 'category', 'tasks')
        list_display = ['title', 'ref', 'query', 'category', 'tasks']
        formfield_overrides = {
                models.CharField: { 'widget': LargeTextInput },
                models.TextField: { 'widget': LargeTextarea },
        }

class ContentAdmin(admin.ModelAdmin):
        list_filter = ('title', 'grammar_ref', 'source_lang')
        list_display = ('title', 'content_preview', 'grammar_ref', 'all_related_content')
        filter_vertical = ('related_content',)
        list_display_links = ('title',)

        formfield_overrides = {
                models.CharField: { 'widget': LargeTextInput },
                models.TextField: { 'widget': LargeTextarea },
        }

class TaskAdmin(admin.ModelAdmin):
        list_display = ('name', 'endpoint', 'success_msg', 'hint_msg')  
        list_display_links = ('name',)

        formfield_overrides = {
                models.CharField: { 'widget': LargeTextInput },
                models.TextField: { 'widget': LargeTextarea },
        }

class TaskSequenceAdmin(admin.ModelAdmin):
        list_display = ('name', 'all_tasks')

        formfield_overrides = {
                models.CharField: { 'widget': LargeTextInput },
                models.TextField: { 'widget': LargeTextarea },
        }

class TaskContextAdmin(admin.ModelAdmin):
        list_display = ('task', 'task_sequence', 'order', 'target_accuracy', 'max_attempts')
        list_editable = ('order',)
        ordering = ('task_sequence', 'order')

        formfield_overrides = {
                models.CharField: { 'widget': LargeTextInput },
                models.TextField: { 'widget': LargeTextarea },
        }

class CategoryAdmin(admin.ModelAdmin):
        list_display = ('name', 'graphic')

        formfield_overrides = {
                models.CharField: { 'widget': LargeTextInput },
                models.TextField: { 'widget': LargeTextarea },
        }

class LanguageAdmin(admin.ModelAdmin):
        list_display = ('name', 'local_name', 'locale', 'short_code', 'direction', 'modern')

        formfield_overrides = {
                models.CharField: { 'widget': LargeTextInput },
                models.TextField: { 'widget': LargeTextarea },
        }

class AppUserAdmin(admin.ModelAdmin):
        list_display = ('username', 'first_name', 'last_name', 'last_login', 'lang_learning', 'lang_speaking')

        formfield_overrides = {
                models.CharField: { 'widget': LargeTextInput },
                models.TextField: { 'widget': LargeTextarea },
        }


admin.site.register(AppUser, AppUserAdmin)
admin.site.register(Language, LanguageAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Grammar, GrammarAdmin)
admin.site.register(Content, ContentAdmin)
admin.site.register(Aspect)
admin.site.register(Task, TaskAdmin)
admin.site.register(TaskSequence, TaskSequenceAdmin)
admin.site.register(TaskContext, TaskContextAdmin)
