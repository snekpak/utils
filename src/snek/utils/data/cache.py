# PYTHON: cache
#-----------------------------><-----------------------------#
# -> Author: qodeninja
# -> Date: 11/16
# -> Id: cache
# -> Autobuild: e60069
# -> Desc: DESCRIPTION
#-----------------------------><-----------------------------#
# -> Notes: 
#-----------------------------><-----------------------------#
# -> Standrd Imports: 
import random, json, sys
from re import T
from dotmap import DotMap
#-----------------------------><-----------------------------#
from ..term.printkit import lc, glyph, silly, trace, error, info, warn
from ..helpers import reduce_dict, reserved, get_nested_ref
from ..base.singleton import Singleton
from .cache_abc import CacheProvider


  
#-----------------------------><-----------------------------#

  
class Cache(CacheProvider):
    def __init__(self,**opts):
      self.data = DotMap()
      self.meta = DotMap()
      self.meta.sessions = []
      self.meta.tasks = []
      self._active = 0
      self._last_task = None
      self._out=[]
      
      self._data = DotMap({
        '_meta':{ 
          'sessions':[], 
          'tasks':[],
        },
        '_hive':{  
          #activekey -> { key:val }
        },
      })

      ##----------------------------------------------##

    def clear(self):
      self._data = DotMap({
        '_meta':{ 
          'sessions':[], 
          'tasks':[],
        },
        '_hive':{  
          #activekey -> { key:val }
        },
      })
      self._active = 0
      self._last_task = None
      self._out=[]    
      
        
    ##----------------------------------------------##
    ## Data Block
    
    @property
    def data(self):
        return self._data
      
    @data.setter
    def data(self, val):
        self._data = val


    
    ##----------------------------------------------##
    ## Active
    
    @property
    def active(self):
      return self._active

    @active.setter
    def active(self, val):
      self._active = val


    # @property
    # def active(self, val):
    #   self._active = val

    ##----------------------------------------------##

    def ready(self,ssid=None):
      active = ssid or self.active
      if active != 0 and active in self._data._hive:
        return True
      return False
    

    def start(self):
      self.active = active = gen_id(24)
      self._data._hive[active] = { 
        '_user' : { }, 
        '_vars' : { }, 
        '_out'  : [] 
      } 
      self._data._meta.sessions.append(active)
      return active
    
    
    def end(self,ssid):
      active = ssid or self.active
      if self.is_active(active):
        del self._data._hive[active]
        self._data._meta.sessions.remove(active)
        return active
      
      
    def switch_sss(self,ssid):
      if ssid in self._data._hive:
        self.active = ssid
        return True
      return False
    

    ##----------------------------------------------##
    ## Hive
    
    @property
    def hive(self):
      if self.ready:
        return self._data._hive[self.active]
      return {}
      
      
    @hive.setter
    def hive(self, hive_dict):
      if self.ready:
        self._data._hive[self.active] = hive_dict
        return True
      return False
      

    ##----------------------------------------------##
    ## Vars


    def var(self,k):
      if self.ready():
        hive = self.hive
        return hive['_vars'][k]
      return False
  
      
    def set_var(self,k,v):
      if self.ready():
        hive = self.hive
        hive['_vars'][k] = v
        return True
      return False
      
      
    def user(self,k):
      if self.ready():
        hive = self.hive
        return hive['_user'][k]
      return False

    def set_user(self,k,v):
      if self.ready():
        hive = self.hive
        hive['_user'][k] = v
        return True
      return False

    ##----------------------------------------------##
    ## StoreProvider interface
    
    @reserved
    def add(self,k,v):
      active = self.active
      
      if(active):
        info('sessin is active')
        hive = self.hive
        hive.update({k:v})
    
    @reserved
    def rm(self,k):
      active = self.active
      if(active):
        hive = self.hive
        hive.clear(k)
    
    @reserved
    def upd(self,k,v):
      return self.add(k,v)
    
    @reserved
    def get(self,k):     
      active = self.active
      if(active):
        data = self._data
        return data.get(active,{}).get(k,None)

    @reserved
    def push(self,k,v):
      active = self.active
      if(active):
        data = self._data
        if not isinstance(data.get(active,{}).get(k,None),list):
          data[active][k] = []
        data[active][k].append(v)
        
    @reserved      
    def pushn(self,k,*args):
      active = self.active
      if(active):
        data = self._data
        if not isinstance(data.get(active,{}).get(k,None),list):
          data[active][k] = []
        for v in args:
          data[active][k].append(v)
            
    @reserved      
    def pop(self,k):
      active = self.active
      if(active):
        data = self._data
        if not isinstance(data.get(active,{}).get(k,None),list):
          data[active][k] = []
        return data[active][k].pop()
      
    @reserved
    def popi(self,k,i):
      active = self.active
      if(active):
        data = self._data
        if not isinstance(data.get(active,{}).get(k,None),list):
          data[active][k] = []
        return data[active][k].pop(i)
      
    @reserved  
    def popn(self,k,n):
      active = self.active
      res=[]
      if(active):
        data = self._data
        if not isinstance(data.get(active,{}).get(k,None),list):
          data[active][k] = []
        for i in range(n):
          res.append(data[active][k].pop())
      return res
    
    
    ##----------------------------------------------##

      
    def _cmds(self):
      fxs = [name for name in dir(self) if callable(getattr(self, name)) and not name.startswith("__")]
      print("cache commands:")
      for cmd in fxs:
        print(f"  {cmd}")
        


    ##----------------------------------------------##


    def new_store(self,k):
      h = self.hive
      if not bool(h) and not k in h:
        h[k] = {}
      return 0


    def new_list(self,k):
      h = self.hive
      if not bool(h) and not k in h:
        h[k] = []
      return 0



    ##----------------------------------------------##

    @property
    def last_task(self):
        return self._last_task

    @last_task.setter
    def last_task(self, v):
        self._last_task = v



    def out(self,v=None):
      data = self._out
      if not v:
        if len(data) > 0:
          return data.pop()
        return []
      else:
        data.append(v)
        




    ##----------------------------------------------##
    ## UTILITY
    def noop(self):
      pass
    
    def raw_dump(self):
      return str(self.data)

    def to_json(self):
      return json.dumps(self.data.toDict())





    ##----------------------------------------------##
    ## SET %:<- prop, val


    def set_prop(self, prop, val, ssid=None, **kwargs):
      return self.add(prop,val)
      



    ##----------------------------------------------##
    ## GET %:-> prop

    def get_prop(self, prop, ssid=None, **kwargs):
      return self.get(prop)
    


    ##----------------------------------------------##
    ## DEL %:prop

    def del_prop(self, prop, ssid=None, **kwargs):
      ssid = ssid or self.active
      hive = self._hive(ssid)

      if self.ready(ssid) and prop in hive:
        del hive[prop]


    ##----------------------------------------------##
    ## PUSH key -> [ k1, k2, k3 ]
    ## req: store must be an array
  
    def push_prop(self, prop, val, ssid=None, **kwargs):
      ssid = ssid or self.active
      hive = self._hive(ssid)

      if self.ready(ssid):
          if prop not in hive:
              hive[prop] = []
          if not isinstance(hive[prop], list):
              raise TypeError(f"Cant push. Prop {prop} is not a list.")
          hive[prop].append(val)
      else:
          raise ValueError(f"No session with ID {ssid} found.")



    ##----------------------------------------------##
    ## POP [ k1, k2, k3 ] -> key
    ## req: store must be an array

    def pop_prop(self, prop, ssid=None, **kwargs):
      ssid = ssid or self.active
      hive = self._hive(ssid)

      if self.ready(ssid):
          if prop not in hive:
              return None
          if not isinstance(hive[prop], list):
              raise TypeError(f"Cant pop. Prop {prop} is not a list.")
          return hive[prop].pop()
      raise ValueError(f"No session with ID {ssid} found.")



    ##----------------------------------------------##
    ## TASK STACK

    def push_task(self, task):
      self.meta.tasks.append(task)


    def pop_task(self):
      if self.meta.tasks:
        return self.meta.tasks.pop()
      return None

    def view_task_stack(self):
      return self.meta.tasks[:]

    ##----------------------------------------------##

    def _execute(self, action, **kwargs):
      fx = None  
      imap = {
        "add": self.set_prop,
        "del": self.del_prop,
        "set": self.set_prop,
        
        "get": self.get_prop,
        
        "push": self.push_prop,
        "pop": self.pop_prop,
        "_cmds": self.invoke,
        "dump" : {  "invoke": "to_json"  },
        "tick" : {  "invoke": "noop"   },
        "clear" : {
          "alias": "clear_cache",  
        },
        "init_store"  : self.invoke,
        "init_list"  : self.invoke,
      }

      if action in imap:
        cmd = imap[action]
        if isinstance(cmd, dict):
          #direct alias
          if 'alias' in cmd: fx = cmd.get('alias', action)
          #invoked alias to clean kwargs
          if 'invoke' in cmd:
            fx = cmd.get('invoke', action) 
            kwargs['cmd'] = fx       
            fx = self.invoke
        else:
          fx = cmd

      if not fx:
        raise ValueError(f'Unsupported task cmd [{action}].')
        
      if not callable(fx):
        fx = getattr(self, fx, None)
      
      if not fx or not callable(fx):
          raise ValueError(f'Method [{fx}] not found for action [{action}].')

      trace(f'attempting next task {fx} {kwargs}')
      return fx(**kwargs)


    def _next_task(self, task):

      #trace(f'attempting next task {task.get("cmd")}')
      
      if not task or 'cmd' not in task:
        raise ValueError('Invalid task format.')
      
      ssid = task.get('ssid', self.active)
      cmd = task['cmd']

      #filter keys into new dict
      kwargs = reduce_dict(task,['cmd', 'ssid'])
      kwargs['ssid'] = ssid #want it at the end
      kwargs['cmd'] = cmd

      #trace(f"Executing task {task.get('task_id')} [{cmd}] [{ssid}]")

      ret = self._execute(cmd, **kwargs)
      self.out(ret)
      warn(F"return value {ret}")


    ##----------------------------------------------##


    def process_tasks(self):
      while self.meta.tasks:
        task = self.pop_task()
        #self.last_task = task
        try:
          self._next_task(task)
        except KeyError as e:
          error(f"Invalid key: {e} {e.__traceback__}")
        except AttributeError as e: 
          error(f"Invalid attr key: {e} {e.__traceback__}")
        except Exception as e:
          error(f"Error executing task {task}: {e} {e.__traceback__.tb_lineno}")

      return self


    ##----------------------------------------------##
    #---> could use a refactor

    def parse_command(self, line):

      trace(f'parse command [{line}]')

      parts = line.split(maxsplit=2)  # Split only the first two spaces

      #trace(parts)
      cmd = parts[0]
      prop = None
      value = None

      #cmd prop value
      if len(parts) == 3:
        prop = parts[1]
        raw_value = parts[2]
        # Check if the raw_value seems to be JSON
        #--> JSON needs double quotes oops
        if raw_value.startswith(('"', '[', '{')):
          try:
            value = json.loads(raw_value) 
          except json.JSONDecodeError:
            raise ValueError("Invalid JSON format in command.") 
        else:
          value = raw_value
      elif len(parts) == 2:
      
        prop = parts[1]

      elif len(parts) == 1:
        pass
        #warn(f'task only had one part, direct call? [{line}]')
      else:
        pass
        #not a json thing to parse?

      task = {"cmd": cmd }

      if prop is not None: 
        task['prop'] = prop
        
      if value is not None: 
        task['val'] = value
        
      if 'ssid' not in task: 
        task['ssid'] = self.active
        
      if 'task_id' not in task:  
        task['task_id'] = gen_id(12)

      trace(f'stack: {task}')

      self.push_task(task)
      return task
    

    ##----------------------------------------------##

    def write(self,command):
      #try:
      task = self.parse_command(command)
      self.last_task = task
        #return task
      # except Exception as e:
      #   error(f"Error writing: {e} {e.__traceback__.tb_lineno}")
      #   #return False
      return self


    ##----------------------------------------------##


    def invoke(self, **kwargs):
      
      #these shouldnt be passed for empty fxs
      cmd = kwargs.pop('cmd',None)
      task_id = kwargs.pop('task_id',None)
      ssid = kwargs.pop('ssid',None)
      
      #info(f'invoking! {cmd}')
      warn(f'proxy function invoke called [{cmd}] [{task_id}] [{ssid}] [{kwargs}]')
      
      fx = getattr(self, cmd, None)
      if fx:
        if len(kwargs) == 0:
          return fx()
        else:
          return fx(**kwargs)
      else:
        error(f'FX [{cmd}] not found')
        # Consider raising an exception or returning a default value here.
        raise ValueError(f'Function [{cmd}] not found')


    def commit(self):
      trace('cache commit...')
      return self.process_tasks()


    ##----------------------------------------------##

    # Persistence
    def save_to_file(self, filename):
      with open(filename, 'w') as f:
        json.dump(self.data.toDict(), f)

    def load_from_file(self, filename):
      with open(filename, 'r') as f:
        self.data = DotMap(json.load(f))


                #---> fin <---#

    
  #-----------------------------><-----------------------------#
  # -> Exports: 

  #-----------------------------><-----------------------------#


def gen_id(size=24):
  return random.getrandbits(size)


##----------------------------------------------##
## Static Cache instance



class StaticCache(Cache):
  
  _inst = {}
  
  def __init__(self):
      super().__init__()
  
  def __call__(cls, *args, **kwargs):
    if cls not in cls._inst:
      cls._inst[cls] = super(Singleton, cls).__call__(*args, **kwargs)
    return cls._inst[cls]

        
static_cache = StaticCache()


#decorator
def cache_access(fx):
  def wrapper(self, *args, **kwargs):
    if(not static_cache.ready()):
      error('Error: session uninitated, cannot process cache')
      return None
    return fx(self, *args, **kwargs)
  return wrapper


#-----------------------------><-----------------------------#
# -> Driver: 

#-----------------------------><-----------------------------#

def driver():
  cache = Cache()
  cache.start()
  if cache.ready(): 
    
    info('cache is ready')    
    cache.add('username','John')
    cache.set_var('x',1)
    cache.set_var('x',2)
    print(cache.var('x'))
    print(cache.raw_dump())
    
  else:
    warn('cache not ready',cache.active)
    
    
  complex_obj = {
    "data" : {
      "model": "text-davinci-003",
      "text": "Translate the following English text to French: 'Hello, how are you today?'",
      "max": 60,
      "temp": 0.7,
      "top_p": 1,
      "freq": 0.0,
      "pres": 0.0,
    },
    "likes": { "boog" : [ 1,2,3,4,5 ] },
    "flavors": { 
      'stawberry': [ 1,2,3], 
      'chocolate': [5,99,100], 
      'vanilla': [ 93,99,23 ]
    },
    "family" : {
        "gonzales" : {
            "females" : [ { "name": "lisa", "age": 33 }, { "name": "mama", "age": 99 } ],
            "males" : [ { "name": "papa", "age": 99 }, { "name": "john", "age": 33 } ],
            "other" : [ { "name": "sister", "age": 11 }, { "name": "brother", "age": 22 } ],
        }
    }
  }
  
  parent, key = get_nested_ref(complex_obj, 'data.max')
  print(parent[key])
  
  parent, key = get_nested_ref(complex_obj, 'flavors.vanilla[0]')
  print(parent[key])  
  
  parent, key = get_nested_ref(complex_obj, 'family.gonzales.males[1].name')
  print(parent[key])  
  
  
  

def driverX():
  # Usage
  cache = Cache()
  ssid = cache.create_session()

  
  # print(ssid)
  # cache.set_prop("username", "John")
  # cache.parse_command('push users JohnX')
  # cache.parse_command('push users AppleGirl')
  # cache.parse_command('push users AppleMama')
  # cache.process_tasks()
  # cache.write('tick').commit()

  # cache.parse_command('push prompt {"msg":"lady had a bug in her hole"}')
  # cache.parse_command('push prompt {"msg":"what shall we do oh no"}')
  # cache.process_tasks()
  # cache.write('tick').commit()
  
  # print(cache.get_prop("username"))  # Outputs: John
  
  
  # print(cache.to_json())





