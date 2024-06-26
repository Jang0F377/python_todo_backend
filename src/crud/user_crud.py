from sqlalchemy.orm import Session
from typing import Union
from ..models.user_model import User
from ..schemas import user_schema
from ..services.password_hasher import PasswordHasher
from fastapi.security import (
    SecurityScopes,
)
from ..schemas.token_schema import TokenData
from fastapi import Depends, HTTPException, Security, Request
from typing import Annotated
from ..services.jwt_service import JWTService
from pydantic import ValidationError
from jwt import exceptions


jwt = JWTService()


def get_user(db: Session, user_id: int) -> user_schema.User:
  """CRUD function to query user by user_id

  Args:
      db (Session): DB Instance
      user_id (int): The id to query

  Returns:
      user_schema.User: The user object
  """
  return db.query(User).filter(User.id == user_id).first()



def get_user_by_username(db: Session, username: str) -> user_schema.User:
  """CRUD function to query user by username

  Args:
      db (Session): DB Instance
      username (str): The username to query

  Returns:
      user_schema.User: the user object
  """
  return db.query(User).filter(User.username == username).first()
  

def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> list[user_schema.User]:
  """CRUD function to return all users

  Args:
      db (Session): DB Instance
      skip (int, optional): Offset to apply to the returned query. Defaults to 0.
      limit (int, optional): Limit to how many items returned. Defaults to 100.

  Returns:
      list[user_schema.User]: List of all users
  """
  return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user: user_schema.UserCreate, hasher: PasswordHasher) -> user_schema.User:
  """CRUD function to add a new user to the DB

  Args:
      db (Session): DB Instance
      user (user_schema.UserCreate): user object to add
      hasher (PasswordHasher): PasswordHasher Instance

  Returns:
      user_schema.User: The newly created user object
  """
  hashed_password = hasher.hash_password(user.password)
  username = user.username.lower()
  user_to_save = User(username=username, hashed_password=hashed_password)
  db.add(user_to_save)
  db.commit()
  db.refresh(user_to_save)
  return user_to_save


def authenticate_user(db: Session, username: str, password: str, hasher: PasswordHasher) -> Union[user_schema.User, bool]:
  """CRUD helper function that returns the authenticated user or false if password is incorrect

  Args:
      db (Session): DB Instance
      username (str): The username to authenticate with
      password (str): The password to authenticate with
      hasher (PasswordHasher): PasswordHasher Instance

  Returns:
      Union[user_schema.User, bool]: User object or False
  """
  user = db.query(User).filter(User.username == username).first()
  if user is None:
    return False
  if not hasher.compare_passwords(password, user.hashed_password):
    return False
  
  return user
  
  
def get_current_user(request: Request, security_scopes: SecurityScopes, token: Annotated[str, Depends(jwt.oauth2_scheme)]) -> user_schema.User:
  """CRUD helper function to return the currently authenticated user parsing the token

  Args:
      request (Request): Need this to be able to use DB Instance
      security_scopes (SecurityScopes): Permissions for routes
      token (Annotated[str, Depends): Bearer token used for authentication

  Raises:
      credentials_exception: 401 - Raises if credentials could not be validated.
      HTTPException: 401 - Raises if user has insufficient permissions for route

  Returns:
      user_schema.User: The authenticated user object
  """
  if security_scopes.scopes:
      authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
  else:
      authenticate_value = "Bearer"
  credentials_exception = HTTPException(
      status_code=401,
      detail="Could not validate credentials",
      headers={"WWW-Authenticate": authenticate_value},
  ) 
  try:
    payload = jwt.decode_token(given_token=token)
    username: str = payload.get('sub')
    if username is None:
      raise credentials_exception
    token_scopes = payload.get('scopes', [])
    token_data = TokenData(scopes=token_scopes, username=username)    
  except (exceptions.DecodeError, ValidationError):
    raise credentials_exception
  user = get_user_by_username(request.state.db, username)
  if user is None:
    raise credentials_exception
  for scope in security_scopes.scopes:
    if scope not in token_data.scopes:
      raise HTTPException(
        status_code=401,
        detail='Insufficient permissions'
      )
  return user
    
    
def get_current_active_user(current_user: Annotated[User, Security(get_current_user, scopes=["basic"])]) -> user_schema.User:
  return current_user