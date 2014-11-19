
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


    
"""
Sort function for returning words ordered by CTS if index on neo4j nodes enables reuse of deleted node's ids.
"""
def sort_words(array):
        
    if array == []:
        return []
    else:
        pivot = array[0]
        lesser = sort_words([x for x in array[1:] if
                             int( x['CTS'].split(':')[len(x['CTS'].split(':'))-1] )
                             < 
                             int(pivot['CTS'].split(':')[len(pivot['CTS'].split(':'))-1])
                             ])
        greater = sort_words([x for x in array[1:] if
                              int(x['CTS'].split(':')[len(x['CTS'].split(':'))-1])
                              >= 
                              int(pivot['CTS'].split(':')[len(pivot['CTS'].split(':'))-1])
                              ])
        return lesser + [pivot] + greater


"""
Sort function for returning sentences ordered by CTS if index on neo4j nodes enables reuse of deleted node's ids.
"""
def sort_sentences(array):
        
    if array == []:
        return []
    else:
        pivot = array[0]
        lesser = sort_sentences([x for x in array[1:] if less_than(x, pivot)])
        greater = sort_sentences([x for x in array[1:] if greater_equal(x, pivot)])
        return lesser + [pivot] + greater
    
"""
Operators for sentence ordering based on book:chapter:sentence number
"""
def less_than(left, pivot):
    
    # if sorting on at least sentence list is done, you might wan to check here of a object or only dictionary is handed over
    # (senteces within a document or words within a sentence are just dict; whereas on sentence or world list, the elements to compare are objects -> see utils 
    left_arr = left['CTS'].split(':')[len(left['CTS'].split(':'))-1].split('.')
    pivot_arr = pivot['CTS'].split(':')[len(pivot['CTS'].split(':'))-1].split('.')
            
    if int(left_arr[0]) > int(pivot_arr[0]):
        return False
    elif int(left_arr[0]) < int(pivot_arr[0]):
        return True
    else:
        if int(left_arr[1]) > int(pivot_arr[1]):
            return False
        elif int(left_arr[1]) < int(pivot_arr[1]):
            return True
        else:
            if int(left_arr[2]) >= int(pivot_arr[2]):
                return False
            else:
                return True             
    return False 
            
def greater_equal(right, pivot):
   
    right_arr = right['CTS'].split(':')[len(right['CTS'].split(':'))-1].split('.')
    pivot_arr = pivot['CTS'].split(':')[len(pivot['CTS'].split(':'))-1].split('.')      
                
    if int(right_arr[0]) < int(pivot_arr[0]):
        return False
    elif int(right_arr[0]) > int(pivot_arr[0]):
        return True
    else:
        if int(right_arr[1]) < int(pivot_arr[1]):
            return False
        elif int(right_arr[1]) > int(pivot_arr[1]):
            return True
        else:
            if int(right_arr[2]) < int(pivot_arr[2]):
                return False
            else:
                return True             
    return False
    
    
    
    
    