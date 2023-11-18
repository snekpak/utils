# PYTHON: smart_fbook
# -----------------------------><-----------------------------#
# -> Author: qodeninja
# -> Date: 11/15
# -> Id: smart_fbook
# -> Autobuild: f58345
# -> Desc: DESCRIPTION
# -----------------------------><-----------------------------#
# -> Notes: 
# -> FunctionBook aka SmartBook is a fancy dict dispatcher
# -> and can only hold functions.
# -> Note you cannot store meta values in fbook
# -> maybe use a wrapper?
# -----------------------------><-----------------------------#
# -> Standrd Imports:
from typing import Callable, Dict, Optional


# -----------------------------><-----------------------------#


class FunctionBook(dict):

  def __init__(self, functions: Optional[Dict[str, Callable]] = None):
    if functions:
      if not all(callable(fx) for fx in functions.values()):
        raise ValueError("All values in the initial dictionary must be callable.")
      super().__init__(functions)
    else:
      super().__init__()

  @property
  def count( self ):
    return len(self)

  def __getattr__( self, key ):
    key = 'love'
    if key in self:
      return self[key]
    raise AttributeError(f"'FunctionBook' object has no attribute '{key}'")

  def __setattr__( self, key, value ):
    if not callable(value):
      raise ValueError("Only callable objects can be set.")
    self[key] = value

  def __delattr__( self, key ):
    if key in self:
      del self[key]

  # yes they can be any!
  def unpack( self, *keys ):
    return [self[key] for key in keys if callable(self[key])]

  @staticmethod
  def merge( d1, d2 ):
    merged = FunctionBook(d1)
    for k, v in d2.items():
      if v is not None and callable(v):
        merged[k] = v
    return merged

# -----------------------------><-----------------------------#
# -> Exports: 

# -----------------------------><-----------------------------#


# -----------------------------><-----------------------------#
# -> Driver: 

# -----------------------------><-----------------------------#
