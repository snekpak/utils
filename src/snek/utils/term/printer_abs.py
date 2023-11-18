# PYTHON: printer_abs
#-----------------------------><-----------------------------#
# -> Author: qodeninja
# -> Date: 11/15
# -> Id: printer_abs
# -> Autobuild: 41e1b1
# -> Desc: DESCRIPTION
#-----------------------------><-----------------------------#
# -> Notes: 
# -> not a true logger, just a term printer to stderr
# -> json dumps for data printer
# -> refactor me
#-----------------------------><-----------------------------#
# -> Standrd Imports: 
import sys, pprint
from json import dumps 
#-----------------------------><-----------------------------#

from .escape import escape_parts, escape_wrap, escape_code, text_pad, pretty
from .const import LEVEL as level, GLYPH as glyph, TDIR as tdir, LC as lc
from ..smart.enum import enum_lookup
from ..smart.obj import SmartObject, smart_merge

##----------------------------------------------##    


class Printer:

  """ Printer starts off in LEVEL.SILENT """
  
  config = { 'level' : level.SILENT }
  
  def __init__(self,print_id,lev, **opts):
    opts = SmartObject(**opts)
    self.id = print_id
    self.level  = lev
    self.prefix = opts.prefix = str(opts.prefix)

    #auto set the fg color if its a log color type
    #TODO:auto set color based on name match
    
    # if lev and not 'fg' in opts:
    #   name = enum_lookup(level,lev)
    
    #TODO:maybe oneday prefix render but for now too tricky
    # if 'pfg' in opts and 'prefix' in opts:
    #   self.prefix = opts.prefix = Printer.prefix_render(opts.pfg,opts.prefix)

    #TODO:keep track of instances and return inst from cls
    #similar to logger
    
    opts.style, opts.code = Printer._escapes(**opts)
    self.opts = opts


##----------------------------------------------##    

  """ Get instance printer escapes """
  def opt(self,key):
    return self.opts.get(key,None)

  def set_opt(self,key,value):
    return self.opts.get(key,value)

  """ Set instance LEVEL """
  def set_level(self, lev):
    self.level = lev
    self.opts.level = lev 
  
##----------------------------------------------##    

  """ Factory creates a new instance """
  @classmethod
  def factory(cls, print_id, lev=level.DISABLED, **opts):
    return cls(print_id, lev, **opts)
    
  @classmethod
  def set_conf(cls, key, val):
    cls.config[key] = val
    
  @classmethod
  def get_conf(cls, key):
    return cls.config.get(key,None)
    
  """ Used by init """
  @classmethod        
  def _escapes(cls, **opts):
    return escape_parts(**opts)
   
  """ Set class LEVEL """
  @classmethod
  def set_global_level(cls, val):
    cls.config['level'] = val
    
  
##----------------------------------------------##    

  """ Test for printable """

  def can_print(self):    
    if Printer.config.get('level') == level.DISABLED: return True
    if self.level == level.DISABLED: return True
    if self.level >= Printer.config.get('level'): return True
    return False
    
##----------------------------------------------##    
  """ Direct call; banners and dumps via kwargs """
    
  def __call__(self, *msgs, **opts):
    mesg_str=data_str=''
    
    if msgs:
      msgs = list(msgs) #convert to list pls
      __ = smart_merge( self.opts , opts ) 
      opts = SmartObject(**__) #turn to smart object
      opts.prefix = str(opts.prefix)
      
      #if Printer.config and self.level >= Printer.config.level:
      if self.can_print():
        
        # if instance allows banner or user asks for banner
        if 'banner' in opts and opts.banner is not tdir.DISABLED:
          banner_str = Printer.banner_printer(msgs.pop(0), **opts)
          stderr(banner_str)
        msg=''
    
        nl="\n{opts.prefix} " if opts.nl else "" #multilist prefix

        #prefix up the messages
        if msgs: msgs[0] = f"{opts.prefix + ' ' if opts.prefix else ''}{msgs[0]}"
        if len(msgs) >= 1:
          msg = f'{nl} '.join(str(m) for m in msgs)

        #pretty data dumper
        if 'data' in opts:
          data_str = Printer.data_printer(**opts)
          if len(msg) >0:
            msg = f'\n'.join([msg, data_str])
          else: msg = data_str
  
        if len(msg) > 0:
          #codify all the things
          if not 'static' in opts:
            _code,_style = Printer._escapes(**opts)
          else:
            _code = opts.code
            _style = opts.style  
          _code,_end = escape_wrap(_code,_style)
          msg = f"{_code}{msg}{_end}"
          stderr(msg)
      else:
        if Printer.get_conf('debug_mode'):
          stderr(f'\033[38;5;238m{glyph.DOTS}printer silenced {glyph.DOTS} ({self.level}) \033[0m')
        pass

##----------------------------------------------##    

  """ Sub Printers on the class level """
  
  @classmethod
  def data_printer(cls, **opts):
    data_str=''    
    data=opts.get('data',{})
    pretty=opts.get('pretty',None)
    border=opts.get('border',None)  
    if data and pretty:
      data_str="\n"+dumps(data, indent=1)+"\n"
      if border: 
        data_str=f'{glyph.LINE}'.join(['',data_str,''])
    elif data:
      data_str=pprint.pformat(data,compact=True)
    return data_str

  @classmethod
  def banner_printer(cls, this_message, **opts):
    opts = SmartObject(**opts) 
    opts.prefix = str(opts.prefix)
    opts.tdir = opts.banner 
    _msg=f"{ str(opts.prefix) + ' ' if opts.prefix else ''}{this_message}"
    _ban = text_pad(_msg, **opts)      
    _code = escape_code(bg=opts.fg,fg=0)
    _code,_end = escape_wrap(_code,opts.style,True)
    _ban=f"{_code}{_ban}{_end}" #with flood tail
    return _ban


#-----------------------------><-----------------------------#
# -> Exports: 

#-----------------------------><-----------------------------#

class InvalidLevelError(Exception):
  def __init__(self, message="Unsupported printer LEVEL"):
    self.message = message
    super().__init__(self.message)

  
##----------------------------------------------##    
  
def stderr(*args):
  print(*args,file=sys.stderr)
  

def set_printer_level(this):
  enum = enum_lookup(level,this)
  if not enum:
    raise InvalidLevelError(f'Level {this} is not a defined printer level.')

  stderr( f'printer level set ->', enum)
  Printer.set_global_level(this)
  

def get_printer_level():
  return Printer.config.get('level') 

def set_printer_config(key,val):
  if key != 'level':
    stderr(f'printer config {key} ->', val)
    Printer.set_conf(key, val)
  
  
def level_lookup(this):
  return enum_lookup(level,this)  
    
    


#-----------------------------><-----------------------------#
# -> Driver: 
    
  """ Driver for testing Printer class  """ 
  
def driver():

  print('printer driver is here')
  
  #set_printer_level(50)
  
  Printer.set_global_level(level.SILLY)
  #set_printer_level(level.SILLY)
  #Printer.setting('level',level.NOTSET)

  silly = Printer.factory('silly', level.SILLY, fg=lc.SILLY,bg=122,si=True, prefix=glyph.PATCH )
  
  silly('hello mermaid!', banner='ctr')
  
  silly('is she a queen!', 'she just might be a queen', 'ah yes she is!')
  silly('NO NO NO!')
  
  xprint = Printer.factory('plain',level.MESSAGE)
  xprint('hello there XPRINT here to party')
  
  justerrors = Printer.factory('justerror', level.ERROR, fg=lc.ERROR, sb=True, prefix=glyph.CROSS)
  justerrors('hi this is just an error sorry!')
  justerrors('maybe you like errors')
  
  okay = Printer.factory('okay', level.SUCCESS,fg=34,bg=0,prefix=glyph.BOLT, pretty=True, border=True)
  okay('well ok then! hello',data=[1,2,3],pretty=True)
  okay('well yes im pretty!',banner='ctr',data=[1,2,3,4,5])



  justerrors('maybe you like errors', data={
    'res': { 'honey' : { 'arr' : [ 1,2,4,  { 'key' : 111 } ] } }
  }, pretty=True, border=True)
  
  trace = Printer.factory('trace', level.TRACE, fg=lc.TRACE, si=True, prefix=glyph.DOTS)
  
  trace('this is a magic trace')
  trace('the arrow of trace loves you is a magic trace')
  
  print(level.CRITICAL)
  print('can silly print', silly.can_print())
  print('can justerrors print', justerrors.can_print())  
  
  
#-----------------------------><-----------------------------#
