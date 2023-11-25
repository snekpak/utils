# PYTHON: escape
#-----------------------------><-----------------------------#
# -> Author: qodeninja
# -> Date: 11/15
# -> Id: escape
# -> Autobuild: e4e01c
# -> Desc: bunch of term code processing funcs
#-----------------------------><-----------------------------#
# -> Notes: 
# -> utility functions for dynamically generating ansi
# -> terminal and escape codes for colors and styles
#-----------------------------><-----------------------------#
# -> Standrd Imports: 

#-----------------------------><-----------------------------#
from .const import STYLE, ESC, TDIR
from .view import view_pad, view_center
from ..smart.obj import SmartObject


#-----------------------------><-----------------------------#
# -> Exports: theyre all exports, well cept the private ones

#-----------------------------><-----------------------------#


#------------------------------  
# legacy lightweight convenience methods
#TODO: refactor these cuz theyre super fragile

def escape(fg=99,bg=0,inv=False,code=''):
  if fg:
    code += f"\033[38;5;{fg}m"
  if bg:
    code += f"\033[48;5;{bg}m"
  if inv:
    code += "\033[7m"
  return code

def escape_str(code,msg,prefix=''):
  return f"\033[38;5;{code}m{prefix} {msg}\033[0m"

def escape_x(msg, fg_code, bg_code=0, inverse=False, prefix=''):
  code = escape(fg=fg_code,bg=bg_code,inv=inverse)
  return f"""{code}{prefix}{msg}\033[0m"""


def pretty(_,code,prefix=''):
  print(escape_str(code, _, prefix))  


#--------------------------------

def pad_size(text, tdir):
  pad=0
  items = [item.value for item in TDIR]
  if tdir == TDIR.DISABLED: return pad
  if tdir in items :
    if tdir==TDIR.CENTER:
      pad = view_center(text)
    if tdir==TDIR.LEFT or tdir == TDIR.RIGHT:
      pad = view_pad(text)  
  else: pass
  return pad

def text_pad(text,**opts):
  opts = SmartObject(**opts)
  b_dir = opts.tdir
  char = opts.char or ' '
  if TDIR.DISABLED != b_dir:
    _pad = pad_size(text, b_dir)
    _ban = f"{char * _pad}{text}" if b_dir in [TDIR.LEFT, TDIR.CENTER] else f"{text}{char * _pad}"
  else:
    _ban = text
  return _ban
    

#--------------------------------


def escape_banner(msg, bg_code, fg_code):
  banner = f"\033[48;5;{bg_code};38;5;{fg_code}m{msg}\x1b[K\033[0m"
  return banner

def dump_colors(fg=7,per_row=16, pad=0):
  for i in range(256):
    block = escape_x(f"{i:5}", fg, bg_code=i)
    print(' ' * pad + block, end='')
    if (i + 1) % per_row == 0:
      print()

def dump_colors_lum(pad=" "):
  for i in range(256):
    bg_color = f"\033[48;5;{i}m"
    fg_color = f"\033[38;5;{text_lum(i)}m"
    print(f"{bg_color}{fg_color}{pad}{i:3}\033[0m", end="")
    if (i + 1) % 16 == 0:
        print()  # for newline after every 16 colors


#--------------------------------

def _rgb_ansi(code):
  # 16-231 are a 6x6x6 color cube.
  if 16 <= code <= 231:
    code -= 16
    return (
      36 * (code // 36) + 55,
      36 * ((code % 36) // 6) + 55,
      36 * (code % 6) + 55,
    )
  return None

def _luminance(rgb):
  r, g, b = [x / 255.0 for x in rgb]
  for i, c in enumerate([r, g, b]):
    if c <= 0.03928:
      c = c / 12.92
    else:
      c = ((c + 0.055) / 1.055) ** 2.4
    [r, g, b][i] = c
  return 0.2126 * r + 0.7152 * g + 0.0722 * b

def text_lum(code):
  rgb = _rgb_ansi(code)
  if not rgb:
    return 15  # Default to white for simplicity.
  lum = _luminance(rgb)
  return 0 if lum > 0.5 else 15  # 0 is black, 15 is white.


#--------------------------------
# for printer factory mostly

def escape_wrap(code,style,flood=False):
  esc_fld=''
  if flood: esc_fld='\033[K' 
  str_code=f"{ESC.DELIM.value}{style}{code}{ESC.END.value}{esc_fld}"
  str_end=f"{ESC.DELIM.value}{STYLE.X.value}{ESC.END.value}"
  return str_code,str_end
  
def escape_parts(**opts):
  opts = SmartObject(**opts)
  code = opts.code
  style = opts.style
  res = opts.res
  if not opts:
    return '',''
  else:
    if not res:
      style = escape_style(**opts)
      code  = escape_code(**opts)
    else:
      style = f"{STYLE.X};"
    return style,code
    
    
def escape_style(**opts):
  style = opts.get('style', '')
  keys = ['inv', 'su', 'si', 'sd', 'sb', 'res']    
  inv, su, si, sd, sb, res = (opts.get(key) for key in keys)
  if not res:
    style_modifiers = [
      f"{STYLE.B};" if sb else "",
      f"{STYLE.D};" if sd else "",
      f"{STYLE.I};" if si else "",
      f"{STYLE.U};" if su else "",
      f"{STYLE.R};" if inv else ""  # Reverse
    ]
    style += ''.join(style_modifiers)
  return style


def escape_code(**opts):
  code = opts.get('code', '')
  fg, bg, ul, res = (opts.get(key) for key in ['fg', 'bg', 'ul', 'res'])
  if res:
      return ''
  modifs = []
  if bg and not fg:
      fg = text_lum(int(bg) or 0)
  if fg is not None:
    modifs.append(f"{ESC.FG_256}{fg};")
  if bg is not None:
    modifs.append(f"{ESC.BG_256}{bg};")
  if ul:
    modifs.append(f"{ESC.UL_COL}{ul};")
  code += ''.join(modifs)
  return code
    
    


#-----------------------------><-----------------------------#
# -> Driver: 

#-----------------------------><-----------------------------#


  