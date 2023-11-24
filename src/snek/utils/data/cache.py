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
#import asyncio

import atexit

from urllib.parse import unquote

from ..base.singleton import Singleton
from .cache_abc import CacheProvider
from .const import STATUS as status

from asyncio import CancelledError, sleep, create_task, get_event_loop, all_tasks

from redis.asyncio import Redis
from redis.exceptions import RedisError

async def simple_async_function():
  print("Async function started")
  await sleep(1)
  print("Async function completed")

#-----------------------------><-----------------------------#

def connected(method):
    """Decorator to ensure Redis connection is available before method call."""
    async def wrapper(self, *args, **kwargs):
        if not self.store:
          raise Exception("Datastore is not ready")
        return await method(self, *args, **kwargs)
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
      self.config(**opts)
      #atexit.register(self._cleanup)
      #max_ping is in milliseconds
      #heartbeat is in seconds
      
      
    def config(self, **opts):
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
          

    async def disconnect(self):
      if self.store:
        #await self._task.cancel()
        await self.store.close()

      
                
          
    ##----------------------------------------------##
    ## Status Prop
    
    @property
    def status(self):
      return self._status
      
    @status.setter
    def status(self, val):
      
      if(self._status != val):
        self._last = self._status
        print(f'Cache status changed from {self._last} to {val}')
        
      self._status = val

    '''only update status if the prev status is less'''
    def next_status(self,status):
      if status > self.status:
        print(f'Cache status changed from {self.status} to {status}')
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

    async def connect(self, **opts):
      
      port = opts.get('port', self._port)
      host = opts.get('host', self._host)
      heartbeat = opts.get('heartbeat', self._heartbeat)
      max_ping = opts.get('timeout', self._timeout)
      
      print(f'heartbeat is {heartbeat} {self._heartbeat}')
      
      if not self.store:
        self.store = Redis(host=host, port=port, decode_responses=True) #connect to instance
        self.status = status.CONNECTED

        if await self.is_live(): #set status to live
  
          if await self.max_ping(timeout=max_ping): #set status to healthy
            print(f'Connected to Redis at {host}:{port}')
            
            #self._task = create_task(self.heartbeat(interval=heartbeat,timeout=max_ping))
            

            
          else:
            print(f'Unhealthy connection to Redis at {host}:{port}')
        else:
          print(f'Could not connect to Redis at {host}:{port}')

        

        
    async def is_live(self):
        try:
          ret= await self.store.ping()
          if ret:
            if self.status < status.LIVE: self.status = status.LIVE
            return True
          return False
        except (RedisError, ConnectionError, TimeoutError):
          return False
        
        
    @connected          
    async def ping(self):
      if self.store:
        start_time = time.perf_counter()
        await self.store.ping()    
        #if self.status < status.PINGABLE: self.status = status.PINGABLE
        self.next_status(status.PINGABLE)
        duration = time.perf_counter() - start_time
        dur_ms = int(duration * 1000)        
        return dur_ms
        
        
    async def max_ping(self, timeout=500):  
      this_ping = await self.ping() #set status to pingable
      if this_ping < timeout:
        self.status = status.HEALTHY
        return True
      self.next_status(status.PINGABLE)
      return False
        
        

    async def heartbeat(self, interval=30, timeout=500):
        print(f"Starting heartbeat with interval {interval} and timeout {timeout}") 
        
        was_healthy = True
        while True:
          
          print("Running heartbeat...")
          
          is_healthy = await self.max_ping(timeout)
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

          await sleep(interval)
          
    @connected
    async def flush(self):
      await self._store.flushdb()
    
    @connected
    async def size(self):
        return await self.store.dbsize()
        
    @connected
    async def set(self, key, value):
        await self.store.set(key, value)

    @connected
    async def get(self, key):
        return await self.store.get(key)

    @connected
    async def delete(self, key):
        return await self.store.delete(key)

    @connected
    async def update(self, key, value,**opts):
      exists = await self.store.exists(key)
      if exists:
        await self.store.set(key, value)
        return True
      return False
    
    

    @connected
    async def push(self, key, value, left=True):
      if left:
        return await self.store.lpush(key, value)
      else:
        return await self.store.rpush(key, value)
    
    @connected
    async def pop(self, key, left=True):
        if left:
            return await self.store.lpop(key)
        else:
            return await self.store.rpop(key)  
          
          
    @connected
    async def set_hash(self, key, subkey, value):
        return await self.store.hset(key, subkey, value)

    @connected
    async def get_hash(self, key, subkey):
        return await self.store.hget(key, subkey)
        
      
    @connected
    async def keys(self, **opts):
      return await self.find()

    @connected
    async def find(self, pattern='*'):
      async with self.store.client() as conn:
        cursor = b"0"  # start at cursor 0
        keys = []
        while cursor:
          cursor, new_keys = await conn.scan(cursor, match=pattern)
          keys.extend(new_keys)
        return keys
      

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



#-----------------------------><-----------------------------#
# -> Driver: 

#-----------------------------><-----------------------------#


def driver():
  pass
