"""
Category resource for API endpoint
"""
from tastypie import fields
from tastypie.resources import ModelResource
from app.models import Category

class CategoryResource(ModelResource):
    
    class Meta:
        queryset = Category.objects.all()
        allowed_methods = ['get']
