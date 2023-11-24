
#-----------------------------><-----------------------------#
# -> Standrd Imports: 
import sys, os
import asyncio
#-----------------------------><-----------------------------#
#from snek.utils.__ import Cache, cache_driver

#from snek.genx import sentence_driver
#from snek.core.core_main import run as core_run

from snek.utils.__ import Cache, cache_status

def driver():
  print('hi from snek utils')

  
async def simple_async_function():
  print("Async function started")
  await asyncio.sleep(1)
  print("Async function completed")



async def cache_driver():
  cache = Cache(heartbeat=10, max_ping=1000)
  await cache.connect()
  await cache.set('key1','testvalue') 
  val = await cache.get('key1')
  print(val)
  await cache.set('key2','testvalue2') 
  val = await cache.get('key2')
  print(val)
  val = await cache.keys()
  print(val)
  val = await cache.size()
  print(val)
  
  
# -----------------------------><----------------------------- #
# -> Driver: 

if __name__ == '__main__':
  
  #asyncio.run(cache_driver())
  loop = asyncio.get_event_loop()
  
  try:
    
    loop.run_until_complete(cache_driver())
    pending = asyncio.all_tasks(loop=loop)
    group = asyncio.gather(*pending)
    loop.run_until_complete(group)
    
    
  except Exception as e:
    print(f"An error occurred: {e}")
  finally:
    loop.run_until_complete(loop.shutdown_asyncgens())
    loop.close()
  
# -----------------------------><----------------------------- #
