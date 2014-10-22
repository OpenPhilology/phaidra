from app.models import AppUser
from common.utils.serializers import urlencodeSerializer
from common.utils.exceptions import CustomBadRequest
from .authorization import CustomAuthorization

from django.conf.urls import url
from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import _get_new_csrf_key as get_new_csrf_key
from django.contrib.auth.hashers import make_password

from tastypie.authentication import (
    Authentication, BasicAuthentication, SessionAuthentication, 
    MultiAuthentication)
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.utils import trailing_slash
from tastypie.http import HttpUnauthorized

class UserResource(ModelResource):
    raw_password = fields.CharField(attribute=None, readonly=True,
                                    null=True, blank=True)

    lang_learning = fields.ForeignKey('api.language.LanguageResource', 
                                    'lang_learning', full=True, 
                                    blank=True, null=True)

    lang_speaking = fields.ForeignKey('api.language.LanguageResource', 
                                    'lang_speaking', full=True, 
                                    blank=True, null=True)

    class Meta:
        authentication = MultiAuthentication(
            BasicAuthentication(), SessionAuthentication())
        serializer = urlencodeSerializer()
        authorization = CustomAuthorization()
        detail_allowed_methods = ['get', 'patch', 'put',]
        always_return_data = True
        queryset = AppUser.objects.all()
        excludes = ['is_active', 'is_staff', 'is_superuser', 'date_joined',
                    'last_login', 'password']

    def prepend_urls(self):
        params = (self._meta.resource_name, trailing_slash())

        return [
            url(r"^(?P<resource_name>%s)/login%s$" % params, 
                self.wrap_view('login'), name="api_login"),
            url(r"^(?P<resource_name>%s)/logout%s$" % params, 
                self.wrap_view('logout'), name="api_logout")
        ]

    def authorized_read_list(self, object_list, bundle):
        return object_list.filter(id=bundle.request.user.id).select_related()

    def get_list(self, request, **kwargs):
        kwargs['pk'] = request.user.pk

        return super(UserResource, self).get_detail(request, **kwargs)

    def obj_update(self, bundle, request=None, **kwargs):
        bundle = super(UserResource, self).obj_update(bundle, **kwargs)
        field_to_update=[]
        for field_name in self.fields:
            field = self.fields[field_name]
            if field.null and (field_name in request.PATCH):
                if request.PATCH[field_name] is u'':
                    setattr(bundle.obj, field_name, None)
                    field_to_update.append(field_name)
        bundle.obj.save(update_fields=field_to_update)
        return bundle

    def hydrate(self, bundle):
        try:
            raw_password = bundle.data.pop('password')
            if not validate_password(raw_password):
                raise CustomBadRequest(
                    code='invalid_password',
                    message='Your password is invalid.')

            bundle.obj.set_password(raw_password)
        except KeyError:
            pass

        return bundle

    def dehydrate(self, bundle):
        if bundle.obj.pk == bundle.request.user.pk:
            bundle.data['key'] = bundle.obj.api_key.key

        return bundle

    def login(self, request, **kwargs):
        """
        Authenticate a user, create a CSRF token for them, and return the user object as JSON.
        """
        self.method_check(request, allowed=['post'])

        data = self.deserialize(
            request, 
            request.body,
            format=request.META.get('CONTENT_TYPE', 'application/json'))

        username = data.get('username', '')
        password = data.get('password', '')

        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                response = self.create_response(request, {
                    'success': True,
                    'username': user.username
                })

                response.set_cookie("csrftoken", get_new_csrf_key())

                return response
            else:
                return self.error_response(request, {
                        'success': False,
                        'reason': 'disabled',
                    }, response_class=HttpForbidden)
        else:                           
            return self.error_response(request, {
                'error_message': 'Incorrect username or password.',
                'success': False,
            }, response_class=HttpUnauthorized)

    def logout(self, request, **kwargs):
        """ 
        Attempt to log a user out, and return success status.           
        """
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)

        if request.user and request.user.is_authenticated():
            logout(request)
            return self.create_response(request, { 'success': True })
        else:
            return self.create_response(request, { 
                'success': False, 
                'error_message': 'Not authenticated' 
            })
