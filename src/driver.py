
#-----------------------------><-----------------------------#
# -> Standrd Imports: 
import sys, os
import asyncio
#-----------------------------><-----------------------------#
#from snek.utils.__ import Cache, cache_driver

#from snek.genx import sentence_driver
#from snek.core.core_main import run as core_run

from snek.utils.__ import Cache, cache_driver, cache_status

async def driver():
  print('hi from snek utils')
  await cache_driver()


  
  
  
  
  

# -----------------------------><----------------------------- #
# -> Driver: 

if __name__ == '__main__':
  asyncio.run(driver())
  
# -----------------------------><----------------------------- #
