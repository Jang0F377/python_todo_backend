from enum import Enum

class Scopes(Enum):
  BASIC = "R/W on current user"
  ADMIN = "basic + extra endpoints"
  SUPER_ADMIN = 'uninhibited R/W/D'
  
