from tastypie.exceptions import Unauthorized
from tastypie.authorization import ReadOnlyAuthorization

class CustomAuthorization(ReadOnlyAuthorization):

    def read_list(self, object_list, bundle):
        return object_list.filter(pk=bundle.request.user.pk)

    def read_detail(self, object_list, bundle):
        return bundle.obj.pk == bundle.request.user.pk

    def create_list(self, object_list, bundle):
        return []

    def create_detail(self, object_list, bundle):
        raise Unauthorized('You are not allowed to access that resource.')

    def update_list(self, object_list, bundle):
        return object_list.filter(pk=bundle.request.user.pk)

    def update_detail(self, object_list, bundle):
        return bundle.obj.pk == bundle.request.user.pk

    def delete_list(self, object_list, bundle):
        return []

    def delete_detail(self, object_list, bundle):
        raise Unauthorized('You are not allowed to access that resource.')
