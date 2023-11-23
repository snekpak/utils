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
import asyncio

from urllib.parse import unquote

from ..base.singleton import Singleton
from .cache_abc import CacheProvider
from .const import STATUS as status

from redis.asyncio import Redis
from redis.exceptions import RedisError


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

class Cache(): #CacheProvider
    def __init__(self,**opts):
      self._store = None
      self._status = status.UNKNOWN
      self._last = status.UNKNOWN
      #max_ping is in milliseconds
      #heartbeat is in seconds

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


    @property
    def store(self):
      return self._store
      
    @store.setter
    def store(self, val):
      self._store = val
        
        
    ##----------------------------------------------##

    async def connect(self, host="127.0.0.1", port=6379, max_ping=500, heartbeat_interval=30):
      
      if not self.store:
        self.store = Redis(host=host, port=port, decode_responses=True) #connect to instance
        self.status = status.CONNECTED

        if await self.is_live(): #set status to live
  
          if await self.max_ping(timeout=max_ping): #set status to healthy
            asyncio.create_task(self.heartbeat(interval=heartbeat_interval,timeout=max_ping))
          else:
            print(f'Unhealthy connection to Redis at {host}:{port}')
        else:
          print(f'Could not connect to Redis at {host}:{port}')

        
        
    async def disconnect(self):
      if self.store:
        await self.store.close()
        
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
        if self.status < status.PINGABLE: self.status = status.PINGABLE
        duration = time.perf_counter() - start_time
        dur_ms = int(duration * 1000)        
        return dur_ms
        
        
    async def max_ping(self, timeout=500):  
      this_ping = await self.ping() #set status to pingable
      if this_ping < timeout:
        self.status = status.HEALTHY
        return True
      self.status = status.PINGABLE
      return False
        
        

    async def heartbeat(self, interval=30, timeout=500):
        was_healthy = True
        while True:
          
          is_healthy = await self.max_ping(timeout)
          
          if not is_healthy and was_healthy:
              print("Redis became unhealthy!")
              # Trigger actions for when Redis goes offline
              # e.g., retry connection, send notification, etc.
          elif is_healthy and not was_healthy:
              print("Redis connection is healthy again.")
              # Actions for when Redis comes back online
          elif is_healthy and was_healthy:
            print("Redis connection is still healthy.")
            if(self.status < status.READY):
              self.status = status.READY
          else:
            print("Redis connection is still unhealthy.")              
          was_healthy = is_healthy

          await asyncio.sleep(interval)

          
        
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
    async def find(self, key, **opts):
      pass

    @connected
    async def keys(self, **opts):
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


async def driver():
  cache = Cache()
  await cache.connect()
  
  pass
