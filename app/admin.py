from django.contrib import admin
from app.models import Textbook, Unit, Lesson, Slide

class TextbookAdmin(admin.ModelAdmin):
	list_display = ('name')

admin.site.register(Textbook)
admin.site.register(Unit)
admin.site.register(Lesson)
admin.site.register(Slide)

