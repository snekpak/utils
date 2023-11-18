



def driver_suite():
  from ..smart.obj import driver as object_driver
  from ..smart.enum import enum_driver
  object_driver()
  enum_driver()
