

from ..smart.enum import SmartEnum

class STATUS(SmartEnum):
  UNKNOWN=0
  
  DISCONNECTED = 100
  
  #IS_CONNECTED means we have a reference to the server object
  CONNECTED = 200

  # IS_LIVE means we attempted an initial ping and it didnt throw an error
  LIVE=300
  
  # IS_PINGABLE means we sent a second ping and it returned without an timeout error
  PINGABLE=400
  
  # IS_HEALTHY means the ping was within the max_ping threshold
  HEALTHY=500
  
  # IS_READY means we have a healthy connection and are ready to accept requests
  READY=600
