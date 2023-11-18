# PYTHON: sitecustomize
# -----------------------------><-----------------------------#
# -> Author: qodeninja
# -> Date: 11/15
# -> Id: sitecustomize
# -> Autobuild: 9c73ac
# -> Desc: provides debug hooks, use wih care
# -----------------------------><-----------------------------#
# -> Notes: Sitecustomize is called on EVERY python invocation
# -> so it must be used with care. The path for site must
# -> also be on PYTHONPATH in order to work
# -> @bashfx/fx-snek is configured to toggle the PYX_DEBUG flag to
# -> enable execution of the debug hooks when needed.
# -> BTW do not import hooks on one line, they wont work
# -> py 3.11
# -----------------------------><-----------------------------#
# -> Standrd Imports: 
import sys, os

# -----------------------------><-----------------------------#


# -----------------------------><-----------------------------#
# -> Main: 

PYX_DEBUG = int(os.getenv('PYX_DEBUG', 1))


if PYX_DEBUG == 0:
  print('~~SiteCustomize~~')

  # ---------------------------------------------- #
  # -> only import if flag is enabled
  from keeji.debug.hooks import hook_meta
  from keeji.debug.hooks import hook_spy
  # fx spy hook removed
  print('~~ import ~~')
else:
  
  print(f'PYX_DEBUG MODE is OFF')


# -----------------------------><-----------------------------#
