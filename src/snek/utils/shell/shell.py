# PYTHON: shell
#-----------------------------><-----------------------------#
# -> Author: qodeninja
# -> Date: 11/17
# -> Id: shell
# -> Autobuild: 119ddd
# -> Desc: DESCRIPTION
#-----------------------------><-----------------------------#
# -> Notes: 
#-----------------------------><-----------------------------#
# -> Standrd Imports: 
import cmd, json, columnize
from regex import F
#-----------------------------><-----------------------------#
from ..term.logo import logo
from ..term.escape import escape_str, escape_x
from ..term.printkit import(
  level, glyph, 
  trace, error, info, success, warn, pretty, 
  view_clear as clear, 
  set_printer_level, get_printer_level
)

from ..helpers import find_kbv
#from ..__ import static_cache as cache, cache_access

#set_printer_level(0)

#-----------------------------><-----------------------------#
class Shell(cmd.Cmd):
  
  _ssid=-1 #     self.ssid = cache.create_session() 
  _mem={}
  
  shorts = {
    'exit'  : [ 'z', 'q' ,'quit', 'end' ],
    'cmds'  : [ '?', 'cmd', 'menu', 'm' ],
    'clear' : [ 'c', 'cls' ],
  }


  def __init__(self,**opts):
    super().__init__()

    ##self.__cmd_list()
    self.prompt = escape_str(99,f'~~~{glyph.SPARK}> ')
    self._intro=''
    #self.intro = escape_x(logo,99,bg_code=0)


    self._contexts = {}
    self._aliases= {}
    self._forwards = {}
    
    self.sss = 0
    self._id = 'main'
    self._out = None
    self._exit = False

    
    #self.repeat_mode = False
    #self._res = None
    
    if self.id == 'top':
      self._intro = escape_x(logo,99,bg_code=0)



##----------------------------------------------##

  # @property
  # def id(self):
  #     return self._id

  # @property
  # def ssid(self):
  #     return Shell._ssid

  #listen for subshell responses
  @property
  def res(self):
      return self._res

  @res.setter
  def res(self, val):
      self._res = val

##----------------------------------------------##
# shell identifier

  @property 
  def id(self):
    return self._id
  
  @id.setter
  def id(self, val):
    self._id = val

#----------------------------------------------#
# exit flag

  @property 
  def exit(self):
    return self._exit
  
  @exit.setter
  def exit(self, val):
    self._exit = bool(val)
  
#----------------------------------------------#
# parent-level aliases cmd.onecmd

  @property
  def forwards(self):
    return self._forwards

  @forwards.setter
  def forwards(self, val):
    self._forwards = val
    
    
#----------------------------------------------#
# store local data from cache calls

  @property
  def out(self):
    return self._out
  
  @out.setter
  def out(self, val):
    self._out = val


##----------------------------------------------##
# standard commands


##----------------------------------------------##
# cmd hook overrides
    
  def precmd(self, line):
    trace(f"pre")
    return line

  def postcmd(self, stop, line):
    trace(f"post")
    if stop:
      error(f'Exiting {self.id}')
      
    return self.exit or stop


  def preloop(self):
 
    if Shell._ssid==-1 :
      Shell._ssid = 1 #cache.start() 
    else:
      info(f"session is {Shell._ssid}")
      
    if self.id == 'top':
      self._refresh()
    
    trace(f"-> preloop")


  def parseline(self, line):
    #trace(f"parse")
    #cmd, arg, line = super(Shell, self).parseline(line) py2????
    cmd, arg, line = super().parseline(line)
    trace(f"line-> [{cmd}] [{arg}] [{line}]")
    
    return cmd, arg, line


  def do_EOF(self, line):
    self.history = []
    error('EOF!')
    return True


  # def cmdloop(self, intro='le intro'):
  #   while True:
  #     try:
  #       super(Shell, self).cmdloop()
  #       break
  #     except KeyboardInterrupt:
  #       print("^C")

##----------------------------------------------##

  def do_log(self,_):
    lvl = get_printer_level()
    if not _: lvl = level.SILENT if lvl == 0 else level.NOTSET
    else: lvl = int(_)
    set_printer_level(lvl)
    
    
  def do_clear(self,_):
    clear() 
    self._refresh()
    return


  def do_cmds(self,_):
    cmds = self.__cmd_list()
    als = self._aliases
    a_list = [f"{value['ns']}" for value in als.values()]
    all = cmds + a_list
    pretty(f'\n{columnize.columnize(all, displaywidth=30, colsep=" | " )}',99)


##----------------------------------------------##
# handle non-standard cmd use-cases like aliases 
# and shortcuts

  def default(self, line):
    args = line.split()
    cmd = args[0]; #alias

    
#   ---> check for shortcuts
    ref = find_kbv(self.shorts,cmd)
    if ref:
      xxx = f'do_{ref}'
      info(f'found shortcut? {ref}')

#   ---> command path check ctx.cmd
    if '.' in cmd:
      
      ctx, sub_cmd = cmd.split('.')
      if cmd.startswith('@'):
        ctx=ctx[1:]
        
      cli = self.__load_cli(ctx)
      
      if not bool(cli):
        warn(f'Unknown context [{ctx}]')
        return
      else:
        #  cmd = f'do_{sub_cmd}'
        if sub_cmd:
          res = cli.onecmd(f'{sub_cmd} {args[1:]}')
          
        if cmd.startswith('@'):
          #load cmd loop
          if not cli.exit:
            info(f'Jump into subshell {ctx}')
            return self._subloop(cli)
          else:
            warn(f'Subshell [{ctx}] skipped')
            return True


#   ---> alias check
    cli_alias = self.__exec_alias_cmd(cmd,args)
    if cli_alias and hasattr(cli_alias, 'res'):
      success(f'Found alias {cmd} {cli_alias.id}')
      return
    
#   ---> subshell check
    cli_main  = self.__load_cli(cmd)
    if not bool(cli_main):
      warn(f'Unknown commands [{cmd}] [{self.id}]')
      
#   ---> subshell loop
    else:
      trace(f'Found subshell cmd:[{cmd}] {cli_main.id}')
      return self._subloop(cli_main)

        
##----------------------------------------------##

  def _subloop(self,cli):
    cli.cmdloop()
    #error(f'Exited subshell {cli.id} {cli.lastcmd} ')
    if(cli.lastcmd=='z' or cli.exit or self.exit):
      return True    


  def _refresh(self):
    print(self._intro)
    pass
    

  def __print_cmds(self,ref=None):
    target = ref if ref else self
    cmds = self.__cmd_list(target)
    als = target.aliases.keys()
    info(f'{cmds}')
    warn(f'{als}')
    



##----------------------------------------------##

  def do_alias(self, line):
    aliases = self._aliases
    warn("try aliases!")
    for alias, details in aliases.items():
      info(f'{alias} -> {details}')


  def do_q(self, args):
    #print("Exiting.")
    return True
  
  def do_z(self, args):
    self.exit=True
    pretty("Terminating.",1,'⁙') #↯
    warn(self.lastcmd)
    return True
  
  
##----------------------------------------------##




  def __cmd_list(self,cli=None):
    target = cli if cli else self
    cmds=[cmd[3:] for cmd in dir(target) if cmd.startswith("do_")]
    return cmds


  def __load_cli(self,key,loop=False):
    if key in self._contexts:
      ref = self._contexts[key]
      if bool(ref):
        cli = ref.get('cli')
        return cli


  def __load_alias(self,key):
    if key in self._aliases:
      detail = self._aliases[key]
      return detail


  def __exec_alias_cmd(self,alias,args,detail=None,startLoop=False):
    
    detail = self.__load_alias(alias)
    if bool(detail):
      #get alias details
      sub_ctx = detail["context"]
      sub_cmd = detail["cmd"]
      cli = self.__load_cli(sub_ctx,False)

      if hasattr(cli, sub_cmd):
        
        # Execute the corresponding command in the subshell
        #  print(f'unpack? {sub_ctx} {sub_cmd} {args}')
        
        #self.__print_cmds(cli)
        info('args',args)
        #did the subshell say anything?
        cli.res = getattr(cli, sub_cmd)(*args[1:])
        
        #cli.onecmd(f'{sub_cmd} {args[1:]}')
        info("res:subshell-->",cli.res,cli.lastcmd)

        return cli
      else:
        warn(f'Command {sub_cmd} does not belong to context {sub_ctx}')

      #raise LookupError(f"No alias details found for {alias}.")


##----------------------------------------------##


      
    
  def submount(self, commander,  **opts):
    
    subshell = commander(Shell)
    ctx = subshell.id;
    forwards = subshell.forwards if hasattr(subshell, 'forwards') else {}
    
#   ---> namespace 
    if ctx in self._contexts or ctx in self._aliases:
      raise NameError(f'Namspace {ctx} is already defined. Cannot mount!')

    self._contexts[ctx] = { 'cli': subshell }

            
#   ---> mount
    if len(forwards) > 0:

      mtd_cmds = self.__cmd_list()
      mtd_als=list(self._aliases.keys())
      
      for fwd, details in forwards.items():
        this_cmd = details['cmd'][3:] #trim do_

#       ---> cmds must be unique
        if this_cmd in mtd_cmds or this_cmd in mtd_als:
          raise NameError(f'Namespace collision for cmd [{this_cmd}]. Cannot mount [{ctx}]')
        else:
          details['ns'] = f'{ctx}:{this_cmd}'
        if not ctx in details:
          details['context'] = ctx
          
        trace(f'new alias added to shell [{fwd}->{ctx}]')
        self._aliases[fwd] = details


#-----------------------------><-----------------------------#
# -> Exports: `

#-----------------------------><-----------------------------#


#-----------------------------><-----------------------------#
# -> Driver: 

#-----------------------------><-----------------------------#

def driver():
  print("Shell Driver is online")
