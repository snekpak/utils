

from ..smart.enum import SmartEnum
#from dataclasses import dataclass

#reg replace -> '([^']*)'\s*:\s*'([^']*)'  |  \U$1=$2


class LEVEL(SmartEnum):
  SILENT = 99
  CRITICAL = 50
  MESSAGE = 49 
  ERROR = 40
  WARNING = 30
  SUCCESS = 29
  INFO = 20
  DEBUG = 10
  TRACE = 5
  SILLY = 1
  NOTSET= 0
  DISABLED =-1


class LC(SmartEnum):
  CRITICAL = 1
  MESSAGE = 15
  ERROR = 9
  WARNING = 214
  SUCCESS = 34 #from 2 so lum will work
  INFO = 39
  DEBUG = 231
  TRACE = 244
  SILLY = 213
  NOTSET= 6
  DISABLED =15


class GLYPH(SmartEnum):
  BOLT='↯'
  PATCH='⁙'
  HASH='⨳'
  DOTS='…'
  TRI='⧊'
  CROSS='✕'
  UNDERQ='¿'
  LIKE= '♥︎'
  DEAD= '☠️'
  LAM='λ'
  CHECK='✔'
  BOOP='⟐'
  STAR='★'
  SPARK='⟡'
  TIE='⋈'
  INF='∞'
  FLAG='⚑'
  PLUS='✚'
  BOX='⧈'
  BULL='⦿'
  REDO='⟳'
  DOOTS='⫶'
  TIME='⧖'
  NOPE='⨂' #⦻
  MORE='&'
  SQUID='〰️'
  SCRIPT='§'
  
  LINE="-----------------------------"


class STYLE(SmartEnum):
  B=1 #bold
  D=2 #dim
  I=3 #ital
  U=4 #under
  BLINK=5
  R=7 #rev
  HID=8
  S=9 #strike
  X=0 #reset/res
  RES_BOLD=21
  RES_DIM=22
  RES_UNDERLINE=24
  RES_BLINK=25
  RES_REVERSE=27
  RES_HIDDEN=28
  RES_UNDERLINE_COLOR=59


class ESC(SmartEnum):
  DELIM='\x1b['
  END='m'
  FG_256='38;5;'
  BG_256='48;5;'
  FG_RGB='38;2;'
  BG_RGB='48;2;'
  UL_COL='4;58;5;'


class TDIR(SmartEnum):
  LEFT='lt'
  RIGHT='rt'
  CENTER='ctr'
  DISABLED='dis'

