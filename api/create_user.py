from django.contrib.auth.hashers import make_password
from django.utils import translation

from tastypie import fields
from tastypie.authentication import (
    SessionAuthentication, BasicAuthentication, Authentication)
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from tastypie.utils import trailing_slash

from app.models import AppUser
from api.user import UserResource

from common.utils.validation import MINIMUM_PASSWORD_LENGTH, validate_password
from common.utils.exceptions import CustomBadRequest

class CreateUserResource(ModelResource):

    class Meta:
        queryset = AppUser.objects.all()
        resource_name = 'create_user'
        fields = ['username', 'first_name', 'last_name', 'last_login']
        list_allowed_methods = ['post']
        detail_allowed_methods = []
        always_return_data = True
        authorization = Authorization()

    def obj_create(self, bundle, **kwargs):
        REQUIRED_FIELDS = ('email', 'first_name', 'last_name', 
                            'password')

        for field in REQUIRED_FIELDS:
            if field not in bundle.data:
                raise CustomBadRequest(
                    code='missing_key',
                    message=('Must provide {missing_key} when creating a'
                        ' user.').format(missing_key=field))

        email = bundle.data['email']
        username = bundle.data['username']

        try:
            if AppUser.objects.filter(email=email):
                raise CustomBadRequest(
                    code='duplicate_exception',
                    message='That email is already in use.')
            if AppUser.objects.filter(username=username):
                raise CustomBadRequest(
                    code='duplicate_exception',
                    message="That username is already in use.")

        except AppUser.DoesNotExist:
            pass

        raw_password = bundle.data.pop('password')

        if not validate_password(raw_password):
            raise CustomBadRequest(
                code='invalid_password',
                message='Your password is invalid')

        kwargs['password'] = make_password(raw_password)

        return super(CreateUserResource, self).obj_create(bundle, **kwargs)
