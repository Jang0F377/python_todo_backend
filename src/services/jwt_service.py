from jwt import decode, encode,exceptions
from datetime import timedelta, datetime, timezone
from typing import Union
from fastapi import HTTPException, status
import os
from ..constants.user_scopes import Scopes
from fastapi.security import (
  OAuth2PasswordBearer,
)

class JWTService:
  oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl='token',
    scopes={'basic': Scopes.BASIC.value, 'admin': Scopes.ADMIN.value, 'super_admin': Scopes.SUPER_ADMIN.value}
  )
  secret_key: str
  jwt_algorithm: str
  
  def __init__(self) -> None:
    self.secret_key = os.environ.get("SECRET_KEY")
    self.jwt_algorithm = os.environ.get("JWT_ALGORITHM")
    
  
  def create_access_token(self, data: dict, expires: Union[timedelta, None] = None) -> str:
    """Method to create and encode a jwt token

    Args:
        data (dict): Data to encode. includes 'sub', and 'scopes'.
        expires (Union[timedelta, None], optional): Expiration time in minutes. Defaults to None.

    Returns:
        str: The encoded JWT
    """
    to_encode = data.copy()
    
    if expires:
      expiration = datetime.now(timezone.utc) + expires
    else:
      expiration = datetime.now(timezone.utc) + timedelta(minutes=20)
    
    to_encode.update({'exp': expiration})
    
    encoded_jwt = encode(payload=to_encode, key=self.secret_key, algorithm=self.jwt_algorithm,)
    return encoded_jwt
  
  def decode_token(self, given_token: str) -> dict[str, any]:
    """Method to decode jwt tokens

    Args:
        given_token (str): the jwt token to decode

    Raises:
        HTTPException: 401 - Raises if token cannot be decoded

    Returns:
        dict[str, any]: the un-encoded object - sub and scopes for the user
    """
    try:
      payload = decode(jwt=given_token, key=self.secret_key, algorithms=self.jwt_algorithm)
    except (exceptions.DecodeError, exceptions.ExpiredSignatureError):
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="JWT decode err. JWT could be expired."
      )
    return payload
      