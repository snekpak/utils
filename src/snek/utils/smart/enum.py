# PYTHON: smart_enum
#-----------------------------><-----------------------------#
# -> Author: qodeninja
# -> Date: 11/15
# -> Id: smart_enum
# -> Autobuild: fb6728
# -> Desc: DESCRIPTION
#-----------------------------><-----------------------------#
# -> Notes: 
# -> I do not like how pythonic Enums work (yet)
# -> SmartEnum behaves more constant like
#-----------------------------><-----------------------------#
# -> Standrd Imports:
from enum import Enum
#-----------------------------><-----------------------------#



class SmartEnum(Enum):
  def __eq__(self, other):
    if isinstance(other, (int, str)):
      return self.value == other
    elif isinstance(other, SmartEnum):
      return self.value == other.value
    return super().__eq__(other)

  def __int__(self):
    if isinstance(self.value, int):
      return self.value
    raise TypeError(f"Value of {self.name} is not an int")

  def __str__(self):
    return str(self.value)

  def __repr__(self):
    return str(self.value)

  def __gt__(self, other):
      if isinstance(other, (int, str)):
        return self.value > other
      elif isinstance(other, SmartEnum):
        return self.value > other.value
      return NotImplemented

  def __lt__(self, other):
      if isinstance(other, (int, str)):
        return self.value < other
      elif isinstance(other, SmartEnum):
        return self.value < other.value
      return NotImplemented

  def __ge__(self, other):
      if isinstance(other, (int, str)):
        return self.value >= other
      elif isinstance(other, SmartEnum):
        return self.value >= other.value
      return NotImplemented

  def __le__(self, other):
      if isinstance(other, (int, str)):
        return self.value <= other
      elif isinstance(other, SmartEnum):
        return self.value <= other.value
      return NotImplemented


#-----------------------------><-----------------------------#
# -> Exports: 

#-----------------------------><-----------------------------#

def enum_lookup(enum_class, value):
    for member in enum_class:
      if member.value == value:
        return member.name
    return None  # or raise an exception, or handle the not-found case as you wish
  

#-----------------------------><-----------------------------#
# -> Driver: 

#-----------------------------><-----------------------------#
  
def enum_driver():
  
  print('----smart enum----')
  class greeks(SmartEnum):
    ALPHA = 11
    BETA = 22
    GAMMA = 33 
    DELTA = 44
    WARNING = 55


  class alphas(SmartEnum):
    ALPHA = 'A'
    BETA = 'B'
    GAMMA = 'C'
    DELTA = 'D'
    WARNING = 'E' 
  alpha = greeks.ALPHA 
  
  print( 'int type', type(greeks.ALPHA), greeks.ALPHA )
  print( 'int comparison >', type(greeks.ALPHA), greeks.ALPHA > 77 )
  print( 'int comparison =', type(greeks.BETA), greeks.BETA == 22 )
  print( 'str type', type(alphas.ALPHA), alphas.ALPHA )
  print( 'str comparison >', type(alphas.GAMMA), alphas.GAMMA > 'A' )
  print( 'str comparison =', type(alphas.BETA), alphas.BETA == 'B' )
  print( 'self comparison >', type(alphas.GAMMA), alphas.GAMMA > alphas.BETA  )
