
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
Sort function for returning object words ordered by CTS globally if index on neo4j nodes enables reuse of deleted node's ids.
"""
def sort_object_words(array):
        
    if array == []:
        return []
    else:
        pivot = array[0]
        lesser = sort_object_words([x for x in array[1:] if less_than_words(x, pivot)])    
        greater = sort_object_words([x for x in array[1:] if greater_equal_words(x, pivot)])
        return lesser + [pivot] + greater  


"""
Operator functions for globally returning words based on urn:cts:...:book:chapter:sentence:word number
"""
def less_than_words(left, pivot):
    
    left_CTS = left.__dict__['_data']['CTS']
    pivot_CTS = pivot.__dict__['_data']['CTS']
    
    # urn:cts:greekLit:tlg0003.tlg001.perseus-grc    
    left_prefix = left_CTS[:-len(left_CTS.split(':')[len(left_CTS.split(':'))-2]+left_CTS.split(':')[len(left_CTS.split(':'))-1])-1]
    pivot_prefix = pivot_CTS[:-len(pivot_CTS.split(':')[len(pivot_CTS.split(':'))-2]+pivot_CTS.split(':')[len(pivot_CTS.split(':'))-1])-1]
    # 1.89.1
    left_arr = left_CTS.split(':')[len(left_CTS.split(':'))-2].split('.')
    pivot_arr = pivot_CTS.split(':')[len(pivot_CTS.split(':'))-2].split('.')
    # word no within sentence
    left_suffix = left_CTS.split(':')[len(left_CTS.split(':'))-1]
    pivot_suffix = pivot_CTS.split(':')[len(pivot_CTS.split(':'))-1]
    
                
    if left_prefix > pivot_prefix:
        return False
    elif left_prefix < pivot_prefix:
        return True
    else:       
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
                if int(left_arr[2]) > int(pivot_arr[2]):
                    return False
                elif int(left_arr[2]) < int(pivot_arr[2]):
                    return True
                else:
                    if int(left_suffix) >= int(pivot_suffix):
                        return False
                    else:
                        return True        
    return False 
            
def greater_equal_words(right, pivot):
    
    right_CTS = right.__dict__['_data']['CTS']
    pivot_CTS = pivot.__dict__['_data']['CTS']
    
    #urn:cts:greekLit:tlg0003.tlg001.perseus-grc
    right_prefix = right_CTS[:-len(right_CTS.split(':')[len(right_CTS.split(':'))-2]+right_CTS.split(':')[len(right_CTS.split(':'))-1])-1]
    pivot_prefix = pivot_CTS[:-len(pivot_CTS.split(':')[len(pivot_CTS.split(':'))-2]+pivot_CTS.split(':')[len(pivot_CTS.split(':'))-1])-1]
    
    # 1.89.1
    right_arr = right_CTS.split(':')[len(right_CTS.split(':'))-2].split('.')
    pivot_arr = pivot_CTS.split(':')[len(pivot_CTS.split(':'))-2].split('.')

    # word no within sentence
    right_suffix = right_CTS.split(':')[len(right_CTS.split(':'))-1]
    pivot_suffix = pivot_CTS.split(':')[len(pivot_CTS.split(':'))-1]
    
    if right_prefix < pivot_prefix:
        #print "1: " + right_prefix + " is not < " + pivot_prefix
        return False
    elif right_prefix > pivot_prefix:
        #print "1: " + right_prefix + " is > " + pivot_prefix
        return True
    else:             
        if int(right_arr[0]) < int(pivot_arr[0]):
            #print "2: " + right_arr[0] + " is not < " + pivot_arr[0]
            return False
        elif int(right_arr[0]) > int(pivot_arr[0]):
            #print "2: " + right_arr[0] + " is > " + pivot_arr[0]
            return True
        else:
            if int(right_arr[1]) < int(pivot_arr[1]):
                #print "3: " + right_arr[1] + " is not < " + pivot_arr[1]
                return False
            elif int(right_arr[1]) > int(pivot_arr[1]):
                #print "3: " + right_arr[1] + " is > " + pivot_arr[1]
                return True
            else:
                if int(right_arr[2]) < int(pivot_arr[2]):
                    #print "4: " + right_arr[2] + " is not < " + pivot_arr[2]
                    return False
                elif int(right_arr[2]) > int(pivot_arr[2]):
                    #print "4: " + right_arr[2] + " is > " + pivot_arr[2]
                    return True
                else:
                    if int(right_suffix) < int(pivot_suffix):
                        #print "5: " + right_suffix + " is not < " + pivot_suffix
                        return False
                    else:
                        #print "5: " + right_suffix + " is >= " + pivot_suffix
                        return True             
    return False

    
"""
Sort function for returning words ordered by CTS within a sentence if index on neo4j nodes enables reuse of deleted node's ids.
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
                              int( x['CTS'].split(':')[len(x['CTS'].split(':'))-1] ) 
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
Operators for sentence ordering based on urn:cts:...:book.chapter.sentence number
"""
def less_than(left, pivot):
    
    try:
        left_CTS = left['CTS']
        pivot_CTS = pivot['CTS']
    # in except, the sentence is an object from the sentence resource, not a dict attribute from the document resource
    except:
        left_CTS = left.__dict__['_data']['CTS']
        pivot_CTS = pivot.__dict__['_data']['CTS']
    
    # urn:cts:greekLit:tlg0003.tlg001.perseus-grc    
    left_prefix = left_CTS[:-len(left_CTS.split(':')[len(left_CTS.split(':'))-1])]
    pivot_prefix = pivot_CTS[:-len(pivot_CTS.split(':')[len(pivot_CTS.split(':'))-1])]
    # 1.89.1
    left_arr = left_CTS.split(':')[len(left_CTS.split(':'))-1].split('.')
    pivot_arr = pivot_CTS.split(':')[len(pivot_CTS.split(':'))-1].split('.')
                
    if left_prefix > pivot_prefix:
        return False
    elif left_prefix < pivot_prefix:
        return True
    else:       
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
    
    try:
        right_CTS = right['CTS']
        pivot_CTS = pivot['CTS']
    # in except, the sentence is an object from the sentence resource, not a dict attribute from the document resource
    except:
        right_CTS = right.__dict__['_data']['CTS']
        pivot_CTS = pivot.__dict__['_data']['CTS']
    
    # urn:cts:greekLit:tlg0003.tlg001.perseus-grc
    right_prefix = right_CTS[:-len(right_CTS.split(':')[len(right_CTS.split(':'))-1])]
    pivot_prefix = pivot_CTS[:-len(pivot_CTS.split(':')[len(pivot_CTS.split(':'))-1])]
    # 1.89.1
    right_arr = right_CTS.split(':')[len(right_CTS.split(':'))-1].split('.')
    pivot_arr = pivot_CTS.split(':')[len(pivot_CTS.split(':'))-1].split('.')

    
    if right_prefix < pivot_prefix:
        return False
    elif right_prefix > pivot_prefix:
        return True
    else:             
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
    
    
    
    
    