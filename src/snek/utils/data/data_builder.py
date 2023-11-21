from ..term.printkit import lc, glyph, silly, trace, error, info, warn
from ..helpers import get_nested_ref


class DataBuilder():

    def __init__(self,**opts):
      self._this = None
      self._refs = {
        # x=1, d={}, l=[]
      }
    
    def make(self,kind,key):
      info(f'Making [{kind}] [{key}]')
      if kind == 'dict':
        this=self.new_dict(key)
      elif kind == 'list':
        this=self.new_list(key)
      elif kind == 'var':
        this=self.new_var(key)
      else:
        this=None
        self._this = this
        return this



#--------------------------------------------------

    @property
    def this(self):
      return self._this
    
    @this.setter
    def this(self,val):
      self._this = val

#--------------------------------------------------
  
    def print_refs(self):
      print(self._refs)
      
      
    def load_ref(self,ref,kind=None):
      this = self._refs[ref]
      
      if kind and type(this) != kind:
        warn(f'Loaded ref {ref} type {type(this)} but expected {kind}')
        return None
      
      if this:
        info(f'Loaded ref {ref} type {type(this)}')
        self._this = this
      else:
        warn(f'Could not load ref {ref}')
      return self._refs[ref]

#--------------------------------------------------


    def push_this(self,val):
      this = self._this
      if type(this) != list:
        error(f'Cannot push to non-list {this}')
        return None
        
      this.append(val)
      info(f'Pushed {val} to list {ref}')
      return this

#--------------------------------------------------

    # new var a
    def new_var(self,k,v):
      self._refs[k] = v
      return self._refs[k]
    
    # new list x
    def new_list(self,k):
      self._refs[k] = []
      return self._refs[k]
    
    # new dict y
    def new_dict(self,k):
      self._refs[k] = {}
      return self._refs[k]
    
    
    
    
    # add key,value
    def ref_dict_add(self,k,v):
      self._refs[k] = v


    def dict_store_ref(self,k,ref):
      r = self._refs[ref]
      self.dict_add(k,r)
      

        

    
    # rename key
    # upd key,value
    # rm key
    
    # list refs
    
    # load ref
    # store ref into key
    
    
    # new list
    # push value
    # pop value i
    # rm value i
    
    # push ref into list
    
    # dump
