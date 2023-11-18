# PYTHON: term_view
#-----------------------------><-----------------------------#
# -> Author: qodeninja
# -> Date: 11/15
# -> Id: term_view
# -> Autobuild: c0108f
# -> Desc: meta information about the terminal dims
#-----------------------------><-----------------------------#
# -> Notes: in the desc
#-----------------------------><-----------------------------#
# -> Standrd Imports: 
import os
#-----------------------------><-----------------------------#

def view_clear():
  os.system('cls' if os.name == 'nt' else 'clear')
  return None

def view_width():
  return int(os.getenv('COLUMNS', 80))

def view_height():
  return int(os.getenv('LINES', 24))

def view_center(text):
  width = view_width()
  padding = (width - len(text)) // 2
  return padding

def view_dims():
  width = view_width()
  height = width = view_height()
  return [width, height]

def view_pad(text):
  width = view_width()
  padding = (width - len(text))
  return padding


#-----------------------------><-----------------------------#
# -> Exports: 

#-----------------------------><-----------------------------#
#-----------------------------><-----------------------------#
# -> Driver: 

#-----------------------------><-----------------------------#
