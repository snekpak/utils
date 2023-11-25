# PYTHON: cache
#-----------------------------><-----------------------------#
# -> Author: qodeninja
# -> Date: 11/23
# -> Id: cache
# -> Autobuild: d07036
# -> Desc: DESCRIPTION
#-----------------------------><-----------------------------#
# -> Notes: 
#-----------------------------><-----------------------------#
# -> Standrd Imports: 
import uuid, time
import random, json, sys

from urllib.parse import unquote

from ..base.singleton import Singleton
from .cache_abc import CacheProvider
from .const import STATUS as status

from ..helpers import unpack_line

#from asyncio import CancelledError, sleep, create_task, get_event_loop, all_tasks

from redis import Redis
from redis.exceptions import RedisError

from ..term.printkit import(
  trace, error, info, success, warn 
)


#-----------------------------><-----------------------------#

def connected(method):
    """Decorator to ensure Redis connection is available before method call."""
    def wrapper(self, *args, **kwargs):
        if not self.store:
          warn("Please wait while we connect to the datastore...")
          st = self.connect()
          if st < status.HEALTHY:
            raise Exception("Datastore is not ready")
        return method(self, *args, **kwargs)
    return wrapper

#-----------------------------><-----------------------------#

# Redis(host='localhost', port=6379, decode_responses=True)
# task_id = str(uuid.uuid4())
# redis.set(task_id, response.text)
# decoded_key = unquote(key)

class Cache: #CacheProvider
  
    def __init__(self,**opts):
      self._store = None
      self._task = None
      self._status = status.UNKNOWN
      self._last = status.UNKNOWN
      self._config(**opts)
      #atexit.register(self._cleanup)
      #max_ping is in milliseconds
      #heartbeat is in seconds
      
      
    def _config(self, **opts):
        self._host = opts.get('host', '127.0.0.1')
        self._port = opts.get('port', 6379)
        self._db   = opts.get('db', 0)
        self._heartbeat = opts.get('heartbeat', 30)
        self._timeout = opts.get('max_ping', 500)
        
        
    # def _cleanup(self):
    #   loop = get_event_loop()
    #   if loop.is_running():
    #     loop.run_until_complete(self.disconnect())
    #   else:
    #     loop.close()
          

    def disconnect(self):
      if self.store:
        #self._task.cancel()
        self.store.close()

      
                
          
    ##----------------------------------------------##
    ## Status Prop
    
    @property
    def status(self):
      return self._status
      
    @status.setter
    def status(self, val):
      if(self._status != val):
        self._last = self._status
        trace(f'Cache status changed from {self._last} to {val}')
      self._status = val

    '''only update status if the prev status is less'''
    def next_status(self,status):
      if status > self.status:
        trace(f'Cache status changed from {self.status} to {status}')
        self.status = status
        return True
      return False

    @property
    def store(self):
      return self._store
      
    @store.setter
    def store(self, val):
      self._store = val
        
        
    ##----------------------------------------------##

    def connect(self, **opts):
      
      port = opts.get('port', self._port)
      host = opts.get('host', self._host)
      #heartbeat = opts.get('heartbeat', self._heartbeat)
      max_ping = opts.get('timeout', self._timeout)
      
      #info(f'heartbeat is {heartbeat} {self._heartbeat}')
      
      if not self.store:
        self.store = Redis(host=host, port=port, decode_responses=True) #connect to instance
        self.status = status.CONNECTED
        if self.is_live(): #set status to live
          if self.max_ping(timeout=max_ping): #set status to healthy
            info(f'Connected to Redis at {host}:{port}')
            #self._task = create_task(self.heartbeat(interval=heartbeat,timeout=max_ping))
          else:
            warn(f'Unhealthy connection to Redis at {host}:{port}')
        else:
          warn(f'Could not connect to Redis at {host}:{port}')
          
      return self.status

        

        
    def is_live(self):
        try:
          ret= self.store.ping()
          if ret:
            if self.status < status.LIVE: self.status = status.LIVE
            return True
          return False
        except (RedisError, ConnectionError, TimeoutError):
          return False
        
        
    @connected          
    def ping(self):
      if self.store:
        start_time = time.perf_counter()
        self.store.ping()    
        #if self.status < status.PINGABLE: self.status = status.PINGABLE
        self.next_status(status.PINGABLE)
        duration = time.perf_counter() - start_time
        dur_ms = int(duration * 1000)      
        info(f'ping {dur_ms}ms')  
        return dur_ms
        
        
    def max_ping(self, timeout=500):  
      this_ping = self.ping() #set status to pingable
      if this_ping < timeout:
        self.status = status.HEALTHY
        return True
      self.next_status(status.PINGABLE)
      return False
        
        
    # not using async 
    def heartbeat(self, interval=30, timeout=500):
      print(f"Starting heartbeat with interval {interval} and timeout {timeout}") 
      
      was_healthy = True
      while True:
        
        print("Running heartbeat...")
        
        is_healthy = self.max_ping(timeout)
        if not is_healthy and was_healthy:
            print("Redis became unhealthy!")

        elif is_healthy and not was_healthy:
            print("Redis connection is healthy again.")

        elif is_healthy and was_healthy:
          self.next_status(status.READY)
          
          print(f"Redis connection is still healthy. {self.status}")
        else:
          print("Redis connection is still unhealthy.")     
                    
        was_healthy = is_healthy

        #sleep(interval)
        
    @connected
    def flush(self):
      self._store.flushdb()
    
    @connected
    def size(self):
        return self.store.dbsize()
        
    @connected
    def set(self, key, value):
        self.store.set(key, value)

    @connected
    def get(self, key):
        return self.store.get(key)

    @connected
    def rm(self, key):
        return self.store.delete(key)

    @connected
    def upd(self, key, value):
      exists = self.store.exists(key)
      if exists:
        self.store.set(key, value)
        return True
      return False
    
    

    @connected
    def push(self, key, value, left=True):
      if left:
        return self.store.lpush(key, value)
      else:
        return self.store.rpush(key, value)
    
    @connected
    def pop(self, key, left=True):
        if left:
          return self.store.lpop(key)
        else:
          return self.store.rpop(key)  
          
          
    @connected
    def set_hash(self, key, hash_value):
      return self.store.hset(key, mapping=hash_value)
        
    @connected
    def get_hash(self, key):
      hash_data = self.store.hgetall(key)
      if hash_data:
         hash_data = {key.decode(): value.decode() for key, value in hash_data.items()}
      return hash_data     
    
      
      
        
    @connected
    def set_mhash(self, key, **kwargs):
        return self.store.hmset(key, **kwargs)
        
    @connected
    def get_mhash(self, key, *args):
        return self.store.hmget(key, *args)
        
      
    @connected
    def keys(self):
      return self.find()

    @connected
    def find(self, pattern='*'):
      with self.store.client() as conn:
        cursor = b"0"  # start at cursor 0
        keys = []
        while cursor:
          cursor, new_keys = conn.scan(cursor, match=pattern)
          keys.extend(new_keys)
        return keys
      
    
    @connected
    def dump(self):
      data={}
      for key in self.store.scan_iter():
        data[key] = self.store.get(key)
      return data
      
        
    ##----------------------------------------------##

      
    def _cmds(self,to_str=False):
      fxs = [name for name in dir(self) if callable(getattr(self, name)) and not name.startswith("__")]
      
      fxs.sort()
      if not to_str:
        print("cache commands:")
        for cmd in fxs:
          print(f"{cmd}")
      else:
        return fxs

    ##----------------------------------------------##
    #---> could use a refactor

    def parse(self, line):

      #trace(f'parse command [{line}]')
      ret=None
      line = line.strip()
      cmd,key,p1,p2,p3,p4 = unpack_line(line,6)
      

        
      args = [arg for arg in [p1, p2, p3, p4] if arg is not None]
      trace(f' [{cmd}] [{key}] [{args}]')
  
      # if cmd and cmd.startswith('$'):
      #   args.insert(0,key)
      #   key = cmd[1:]
      
      # size
      if cmd == 'size':
        print(self.size())
      # ping
      elif cmd == 'ping':
        print(self.ping())      
      # keys
      elif cmd == 'keys':
        print(self.keys())
      # set k v
      elif cmd in ['set','add','+']:
        ret = self.set(key,p1)
      # get k 
      elif cmd in ['get','read','@']:
        ret = self.get(key)
        print(ret)
        return ret
      # rm k
      elif cmd in ['del','rm','-']:
        ret = self.set(key,p1)
      # push k v l
      elif cmd in ['push','>']:
        ret = self.push(key,p1)
      # pop k l
      elif cmd in ['pop','<']:
        ret = self.pop(key)
        print(ret)

      
      elif cmd in ['call']:
        warn(f'attempting to call {key}')
                
        fx = getattr(self, key)
        ret = fx(*args)
        print(ret)

      
      # set_hash k sk v
      elif cmd == 'hset':
        print(self.set_hash(key,p1))
      # get_hash k sk
      elif cmd == 'hget':
        ret = self.get_hash(key)

        
      # find 
      elif cmd == 'find':
        print(self.find(key))
      
      
      if ret is not None:
        ret = ret.decode()
        return ret

#-----------------------------><-----------------------------#
# -> Exports: 

#-----------------------------><-----------------------------#



class StaticCache(Cache):
  _inst = {}
  def __init__(self): super().__init__()
  def __call__(cls, *args, **kwargs):
    if cls not in cls._inst:
      cls._inst[cls] = super(Singleton, cls).__call__(*args, **kwargs)
    return cls._inst[cls]

static_cache = StaticCache()

#-----------------------------><-----------------------------#
# -> Driver: 

#-----------------------------><-----------------------------#


def driver():
  pass
