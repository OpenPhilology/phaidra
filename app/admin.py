from django.contrib import admin
from app.models import Language, Category, AppUser, Grammar, Content  

#class TextbookAdmin(admin.ModelAdmin):
#	list_display = ('name')

admin.site.register(AppUser)
admin.site.register(Language)
admin.site.register(Category)
admin.site.register(Grammar)
admin.site.register(Content)

