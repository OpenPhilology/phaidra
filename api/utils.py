
"""
Simple object for creating the instances.
"""        
class DataObject(object):
    
    def __init__(self, id=None):
        
        self.__dict__['_data'] = {}
        
        if not hasattr(id, 'id') and id is not None:
            
            self.__dict__['_data']['id'] = id
       
    def __getattr__(self, name):
        if name.startswith('__'):
            raise AttributeError
        return self._data.get(name, None)

    def __setattr__(self, name, value):
        self.__dict__['_data'][name] = value

    def to_dict(self):
        return self._data