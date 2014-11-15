from tastypie.validation import Validation
import string

class ResourceValidation(Validation):
    
    def is_valid(self, bundle=None, request=None):
        
        # allowed for CTS
        invalidChars = string.punctuation.replace(".", "")
        invalidChars = invalidChars.replace(":", "")
        invalidChars = invalidChars.replace("-", "")
        #allowed for word attributes
        invalidChars = invalidChars.replace("_", "")
        #allowed for ref keys
        invalidChars = invalidChars.replace("#", "")
        
        invalidChars = set(invalidChars)
        errors = {}
        
        for key in request.GET:        
            if any(char in invalidChars for char in request.GET.get(key)):
                errors[key] = ['Invalid.']            
        return errors
