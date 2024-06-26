from pydantic import BaseModel
from typing import Union


# Classes to define the JWT token
class Token(BaseModel):
  access_token: str
  token_type: str
  
class TokenData(BaseModel):
  username: Union[str, None] = None
  scopes: list[str] = []