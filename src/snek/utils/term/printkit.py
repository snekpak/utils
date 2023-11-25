# PYTHON: printkit
#-----------------------------><-----------------------------#
# -> Author: qodeninja
# -> Date: 11/16
# -> Id: printkit
# -> Autobuild: 48f319
# -> Desc: DESCRIPTION
#-----------------------------><-----------------------------#
# -> Notes: 
#-----------------------------><-----------------------------#
# -> Standrd Imports: 

#-----------------------------><-----------------------------#
from .printer_abs import Printer, pretty, set_printer_level, set_printer_config, get_printer_level, level_lookup, level, lc, glyph, stderr
from .logo import logo_bg
from .view import view_clear
from ..smart.fbook import FunctionBook
#-----------------------------><-----------------------------#
# -> Exports: 

#-----------------------------><-----------------------------#

silly   = Printer.factory('silly', level.SILLY, fg=lc.SILLY,bg=0, prefix=glyph.HASH )
trace   = Printer.factory('trace', level.TRACE, fg=lc.TRACE, si=True, prefix=glyph.DOTS, static=True)
info    = Printer.factory('info',  level.INFO,  fg=lc.INFO, bg=0,prefix=glyph.BOOP, static=True)
success = Printer.factory('success',  level.SUCCESS,  fg=lc.SUCCESS, bg=0,prefix=glyph.PLUS, static=True)
warn    = Printer.factory('warn',  level.WARNING, fg=lc.WARNING, prefix=glyph.FLAG, static=True)
error   = Printer.factory('error', level.ERROR, fg=lc.ERROR, prefix=glyph.CROSS, static=True)
fatal   = Printer.factory('fatal', level.CRITICAL, fg=lc.CRITICAL, sb=True, prefix=glyph.BOX, static=True)
banner  = Printer.factory('banner', banner='ctr', bg=33)

#set_printer_level(level.NOTSET)
if get_printer_level() == level.SILENT:
  print("[PRINTKIT] warning: printer level is SILENT.")
  

# for printer in [silly, trace, info, success, warn, error, fatal, banner]:
#   assert callable(printer), f"{printer} is not callable"

def _printer_kit():
  return FunctionBook({
    'silly'   : silly,
    'trace'   : trace, 
    'info'    : info,
    'success' : success,
    'warn'    : warn,
    'error'   : error,
    'fatal'   : fatal,
    'banner'  : banner,
    'clear'   : view_clear
  })


print_kit = _printer_kit()

#-----------------------------><-----------------------------#
# -> Driver: 

#-----------------------------><-----------------------------#

def driver():
  
  print('utils driver is here')
  #printer_driver()
  set_printer_config('debug_mode',True)
  set_printer_level(level.SILLY)
  kit = print_kit
  kit.info('hi there')
  kit.warn('warned yo mama')
  kit.error('error in the house')
  set_printer_level(level.SILENT)

  kit.info('i am the queen')
  kit.fatal('oh no she didnt',fg=11)
  kit.success('i am winning',fg=11)
  kit.silly('im the silliest clown around', prefix=glyph.TIE, fg=11)
  set_printer_level(level.SILLY)
  kit.warn('warned yo mama', prefix=glyph.SPARK, fg=1 )
  set_printer_level(level.SILENT)
  kit.banner.set_level(level.INFO)
  kit.banner('maybe you noticed me', prefix=glyph.LIKE, fg=1)
  kit.banner('a spark in the dark', prefix=glyph.SPARK, fg=33)
  
  set_printer_level(level.SILENT)
  
