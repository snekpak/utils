# PYTHON: smart_obj
#-----------------------------><-----------------------------#
# -> Author: qodeninja
# -> Date: 11/15
# -> Id: smart_obj
# -> Autobuild: 7fdcf4
# -> Desc: DESCRIPTION
#-----------------------------><-----------------------------#
# -> Notes: 
# -> I originally wanted to call this Object lol
# -> until I discovered I could not iterate over callables
# -> then I made functionbook
#-----------------------------><-----------------------------#
# -> Standrd Imports:
import json
#-----------------------------><-----------------------------#


class SmartObject(dict):
    """ Custom dictionary that supports dot notation access and is iterable. """
    """ Note: does not support callables. use Function Book instead """

    def __getattr__(self, key):
      """does not throw a missing key error"""
      return self.get(key, '')

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
      try:
          del self[key]
      except KeyError:
          return None
        
    #function support
    def __iter__(self):
        if any(callable(value) for value in self.values()):
            # Yield only callable items
            return (value for value in self.values() if callable(value))
        else:
            # Default dictionary iteration (over keys)
            return super().__iter__()
        return iter(self.values()) 
      
    def to_json(self):
      return json.dumps(self.__dict__)
    
    def __str__(self):
      return self.to_json()
    
    def unpack(self, keys):
      return [self.get(key) for key in keys]



#-----------------------------><-----------------------------#
# -> Exports: 

#-----------------------------><-----------------------------#

def smart_merge(d1,d2):
  this = {} | d1
  this.update({k: v for k, v in d2.items() if v is not None})
  return this

#-----------------------------><-----------------------------#
# -> Driver: 

#-----------------------------><-----------------------------#

def driver():
  # Example usage
  print('----smart obj----')
  obj = SmartObject({'a': 1, 'b': 2})
  print('dot acess', obj.a)  # Outputs 1

  obj.c = 3
  print('book access',obj['c'])  # Outputs 3

  # Iterating over the dictionary
  for key, value in obj.items():
      print(f"{key}: {value}")

