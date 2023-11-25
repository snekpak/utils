# PYTHON: cache_shell
#-----------------------------><-----------------------------#
# -> Author: qodeninja
# -> Date: 11/16
# -> Id: cache_shell
# -> Autobuild: 38be02
# -> Desc: DESCRIPTION
#-----------------------------><-----------------------------#
# -> Notes: 
#-----------------------------><-----------------------------#
# -> Standrd Imports: 
import json
#-----------------------------><-----------------------------#


from snek.utils.shell.shell import(
  Shell, 
  cache,
  cache_access, 
  trace, success, info, escape_str
)


from snek.genx.gx.gen import next_simple_sentence, next_smart_sentence


#-----------------------------><-----------------------------#
 
 

class CacheShell(Shell):

  def __init__(self,parent):
    super(CacheShell,self).__init__()
    
    self.color = 211
    self.last = ''
    self.prompt = escape_str(self.color,'~⁙cache -> ')
    self.contexts = {}
    self._id = 'cache'
    
    self.forwards = { 
      'ping_cache': {'cmd': 'do_hello_cache', 'desc': 'Ping the cache'} 
    }
        
    
##----------------------------------------------##


  def precmd(self, line):
    trace(f"pre~cache {line}")
    return line
  
#-----------------------------><-----------------------------#
# -> Cache: 

#-----------------------------><-----------------------------#  

  def do_hello_cache(self,**kwargs):
    print("ping.....cache!")
    return "ping hello!"
  
  @cache_access
  def do_about(self,__):
    info("you made a cache call!")
    cache.write('_cmds').commit()
    #warn(cache.session_stat())
    pass
  
  @cache_access
  def do_job(self, cmd):
    cache.write(cmd).commit()
    task = cache.last_task
    success(json.dumps(task))
    out = cache.out()
    success(out)
    print(cache.to_json())

  def do_dump(self, args):
    print(cache.to_json())
    return 

#-----------------------------><-----------------------------#
# -> Generator: 

#-----------------------------><-----------------------------#  


  def do_i(self, args):
    self.do_show_log(1)
    
  def do_gen(self, arg):
    next_simple_sentence()
    pass

  def do_g(self, arg):
    self.do_clear(arg)
    next_simple_sentence()
    pass

  def do_n(self, arg):
    self.do_clear(arg)
    next_smart_sentence()
    pass
  
  
#-----------------------------><-----------------------------#
# -> Exports: 

#-----------------------------><-----------------------------#


#-----------------------------><-----------------------------#
# -> Driver: 

#-----------------------------><-----------------------------#
