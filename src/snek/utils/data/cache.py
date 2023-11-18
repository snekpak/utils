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
from dotmap import DotMap
#-----------------------------><-----------------------------#
from ..term.printkit import lc, glyph, silly, trace, error, info, warn
from ..helpers import reduce_dict
from ..base.singleton import Singleton
from .store import StoreProvider


  
#-----------------------------><-----------------------------#

  
class Cache():
    def __init__(self,**opts):
      self.data = DotMap()
      self.meta = DotMap()
      self.meta.sessions = []
      self.meta.tasks = []
      self._active = 0
      self._last_task = None
      self._out=[]
      
      # self._data = {
        
      #   '_meta':{ 
      #     'sessions':[], 
      #     'tasks':[],
      #   },
      #   '_hive':{    },
      # }

    ##----------------------------------------------##


    # def to_json(self):
    #   info(f'HIVE {repr(self.data)}')
      
    #   print(dict(self.data))

    # def __str__(self):
    #   return self.to_json()
    
    # def dump_json(self):
    #   print(self.to_json())
      
    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, val):
        self._active = val



    @property
    def last_task(self):
        return self._last_task

    @last_task.setter
    def last_task(self, val):
        self._last_task = val



    def out(self,val=None):
      data = self._out
      if not val:
        if len(data) > 0:
          return data.pop()
        return []
      else:
        data.append(val)
      

    # @out.setter
    # def out(self, val):
    #   #data = self._out
    #   if len(self._out) == 0: self._out=[]
    #   self._out.push(val)




    ##----------------------------------------------##


    def raw_dump(self):
      return str(self.data)

    def to_json(self):
      return json.dumps(self.data.toDict())


    ##----------------------------------------------##

    def clear_cache(self, **kwargs):
      data = self.data
      meta = self.meta
      data = DotMap()
      meta = DotMap()
      meta.sessions = []
      meta.tasks = []
      self.active = 0

    ##----------------------------------------------##

    ##----------------------------------------------##
    ## UTILITY
    def noop(self):
      pass
    
    def _cmds(self):
      fxs = [name for name in dir(self) if callable(getattr(self, name)) and not name.startswith("__")]
      print("cache commands:")
      for cmd in fxs:
        print(f"  {cmd}")

    def _hive(self,ssid=None):
      ssid = ssid or self.active
      return self.data[ssid]
        
    def _valid_hive(self,ssid=None):
      ssid = ssid or self.active
      hive = self.data[ssid]
      return not bool(hive) and ssid in self.meta.sessions
    

    def init_store(self,prop,ssid=None):
      hive = self._hive(ssid)
      if not bool(hive) and not prop in hive:
        hive[prop] = {}
      return 0


    def init_list(self,prop,ssid=None):
      hive = self._hive(ssid)
      if not bool(hive) and not prop in hive:
        hive[prop] = []
      return 0


    ##----------------------------------------------##
    ## SESSION CRUD

    ## HAS (requires ssid)
    def has_session(self,ssid):
      return ssid in self.meta.sessions

    ## CREATE SSS
    def create_session(self, init=None):
      ssid = gen_id(24)
      data = self.data
      meta = self.meta
      data[ssid] = init or DotMap()
      meta.sessions.append(ssid)
      self.active = ssid
      self.write('add _user {"connected":0,"name":"","key":""}').commit()
      return ssid
    
    ## DELETE SSS
    def delete_session(self, ssid=None):
      ssid = ssid or self.active
      data = self.data
      meta = self.meta
      if ssid in meta.sessions:
        del data[ssid]
        meta.sessions.remove(ssid)
        return ssid
      return False

    ## GET SSS -> hive. hive is internal 

    def session_stat(self):
      return (self.active!=0)

    def session_start(self):
      return self.create_session()

    def session_end(self):
      return self.delete_session()

    ##----------------------------------------------##
    ## SET %:<- prop, val


    def set_prop(self, prop, val, ssid=None, **kwargs):
      
      #info(f'SET PROP {prop}{val}')
      ssid = ssid or self.active
      hive = self._hive(ssid)
      if self.has_session(ssid):
        hive[prop] = val
        #info(f'HIVE {self.data}')
      else:
        raise ValueError(f"No session with ID {ssid} found.")
      


    ##----------------------------------------------##
    ## GET %:-> prop

    def get_prop(self, prop, ssid=None, **kwargs):
      ssid = ssid or self.active
      hive = self._hive(ssid)

      if self.has_session(ssid):
        data = hive.get(prop, None)
        #self.out(data)
        return data
      #implicit else
      raise ValueError(f"No session with ID {ssid} found.")
    


    ##----------------------------------------------##
    ## DEL %:prop

    def del_prop(self, prop, ssid=None, **kwargs):
      ssid = ssid or self.active
      hive = self._hive(ssid)

      if self.has_session(ssid) and prop in hive:
        del hive[prop]


    ##----------------------------------------------##
    ## PUSH key -> [ k1, k2, k3 ]
    ## req: store must be an array
  
    def push_prop(self, prop, val, ssid=None, **kwargs):
      ssid = ssid or self.active
      hive = self._hive(ssid)
 
      if self.has_session(ssid):
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

      if self.has_session(ssid):
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


# class Hive(StoreProvider):
#   def __init__(self,**opts):
#     pass
  
#   def add(self,k,v):
#     pass
  
#   def rm(self,k):
#     pass
  
#   def get(self,k):
#     pass
  
#   def up(self,**kwargs):
#     pass
  
#-----------------------------><-----------------------------#
# -> Exports: 

#-----------------------------><-----------------------------#


def gen_id(size=24):
  return random.getrandbits(size)


##----------------------------------------------##
## Static Cache instance

#static_cache = Cache()

class StaticCache(Cache, metaclass=Singleton):
    def __init__(self):
        super().__init__()
        
        
static_cache = Cache()


#decorator
def cache_access(fx):
  def wrapper(self, *args, **kwargs):
    if(not static_cache.session_stat()):
      error('Error: session uninitated, cannot process cache')
      return None
    return fx(self, *args, **kwargs)
  return wrapper


#-----------------------------><-----------------------------#
# -> Driver: 

#-----------------------------><-----------------------------#



def driver():
  # Usage
  cache = Cache()
  ssid = cache.create_session()
  
  print(ssid)
  cache.set_prop("username", "John")
  cache.parse_command('push users JohnX')
  cache.parse_command('push users AppleGirl')
  cache.parse_command('push users AppleMama')
  cache.process_tasks()
  cache.write('tick').commit()

  cache.parse_command('push prompt {"msg":"lady had a bug in her hole"}')
  cache.parse_command('push prompt {"msg":"what shall we do oh no"}')
  cache.process_tasks()
  cache.write('tick').commit()
  
  print(cache.get_prop("username"))  # Outputs: John
  
  
  print(cache.to_json())





