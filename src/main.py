from fastapi import FastAPI, Depends, HTTPException, Request, Response
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .models import todo_model,user_model
from .crud import todo_crud, user_crud
from .schemas import todo_schema, user_schema, token_schema
from .database import engine, SessionLocal
from .services import password_hasher,jwt_service
from datetime import timedelta
import os
from .constants.user_scopes import Scopes


ACCESS_TOKEN_EXPIRATION_MINUTES = os.environ.get("ACCESS_TOKEN_EXPIRATION")

# Quick and simplistic way to create db tables
# In prod or real project would likely use something like Alembic
todo_model.Base.metadata.create_all(bind=engine)
user_model.Base.metadata.create_all(bind=engine)


# Init 
app = FastAPI()
password_hasher = password_hasher.PasswordHasher()
jwt = jwt_service.JWTService()

# Middleware Dependency to attach db to request
@app.middleware('http')
async def db_session_middleware(request: Request, call_next):
  response = Response("Error with middleware", status_code=500)
  try:
    request.state.db = SessionLocal()
    response = await call_next(request)
  finally:
    request.state.db.close()
    
  return response
    
# Dependency
def get_db(request: Request):
  return request.state.db
    

@app.post('/login')
def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)) -> token_schema.Token:
  """Endpoint that handles 'logging in' the user

  Args:
      form_data (Annotated[OAuth2PasswordRequestForm, Depends): data must be form-data.
      Can reach username and password via form_data.username | form_data.password
      db (Session, optional): DB instance. Defaults to Depends(get_db).

  Raises:
      HTTPException: status_code=400, if no user is returned from authenticate_user

  Returns:
      token_schema.Token: With two properties 'access_token' and 'token_type'
  """
  user = user_crud.authenticate_user(db=db, username=form_data.username.lower(), password=form_data.password, hasher=password_hasher)
  if not user:
    raise HTTPException(status_code=400, detail='Incorrect username or password')
  data = {
    'sub': user.username,
    'scopes': [str(Scopes.BASIC.name).lower()]
  }
  access_token_expiration = timedelta(minutes=int(ACCESS_TOKEN_EXPIRATION_MINUTES))
  access_token = jwt.create_access_token(data=data,expires=access_token_expiration)
  return token_schema.Token(access_token=access_token, token_type='bearer')
  

@app.post('/users/', response_model=user_schema.User)
def create_user(user: user_schema.UserCreate, db: Session = Depends(get_db)) -> user_schema.User:
  """Endpoint to handle creating a new user

  Args:
      user (user_schema.UserCreate): user creation object with a username, password
      db (Session, optional): DB instance. Defaults to Depends(get_db).

  Raises:
      HTTPException: 400 - Raises if either username/password given are empty
      HTTPException: 400 - Raises if another user with the same username exists

  Returns:
      user_schema.User: the user that was added to the DB. 
  """
  # Catch empty input
  if not user.username or not user.password:
    raise HTTPException(status_code=400, detail="Cannot send empty values for username or password.")
  
  # Check if user already exists
  user_exists = user_crud.get_user_by_username(db=db, username=user.username)
  if user_exists:
    raise HTTPException(status_code=400, detail="Email is already registered, try logging in.")
  
  # Create and return user
  return user_crud.create_user(db=db, user=user, hasher=password_hasher)

@app.get('/users/', response_model=list[user_schema.User])
def get_all_users(db: Session = Depends(get_db), skip: int = 0, limit: int = 100) -> list[user_schema.User]:
  """Endpoint to return all users

  Args:
      db (Session, optional): DB instance. Defaults to Depends(get_db).
      skip (int, optional): Offset to apply to the query. Defaults to 0.
      limit (int, optional): Limit to return. Defaults to 100.

  Returns:
      list[user_schema.User]: Returns a list of users
  """
  users = user_crud.get_all_users(db=db, skip=skip, limit=limit)
  return users


@app.get('/users/me/', response_model=user_schema.User)
def get_active_user(current_user: Annotated[user_schema.User, Depends(user_crud.get_current_active_user)]) -> user_schema.User:
  """Endpoint to return the currently logged in user from JWT

  Args:
      current_user (Annotated[user_schema.User, Depends): Calls the user_crud.get_current_active_user

  Returns:
      user_schema.User: Returns the user from the parsed JWT
  """
  return current_user

@app.get('/users/username/{username}', response_model=user_schema.User)
def get_user_by_username(username: str, db: Session = Depends(get_db)) -> user_schema.User:
  """Endpoint to return a user by username

  Args:
      username (str): The username to query
      db (Session, optional): DB instance. Defaults to Depends(get_db).

  Raises:
      HTTPException: 404 - Raises if no user found by username

  Returns:
      user_schema.User: Returns the user found with username
  """
  user_name = username.lower()
  user = user_crud.get_user_by_username(db=db, username=user_name)
  if user is None:
    raise HTTPException(status_code=404, detail='User not found')
  return user

@app.get('/users/{user_id}', response_model=user_schema.User)
def get_user_by_user_id(user_id: str, db: Session = Depends(get_db)) -> user_schema.User:
  """Endpoint to return user by user_id

  Args:
      user_id (str): The user_id to query
      db (Session, optional): DB instance. Defaults to Depends(get_db).

  Raises:
      HTTPException: 404 - Raises if user not found by user_id

  Returns:
      user_schema.User: Returns the user found by the user_id
  """
  user = user_crud.get_user(db=db, user_id=user_id)
  if user is None:
    raise HTTPException(status_code=404, detail='User not found')
  return user


@app.get('/todos/', response_model=list[todo_schema.ToDo])
def get_all_todos( skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> list[todo_schema.ToDo]:
  """Endpoint to get ALL todos in DB

  Args:
      skip (int, optional): Offset to apply to the query. Defaults to 0.
      limit (int, optional): Limit to number returned . Defaults to 100.
      db (Session, optional): DB Instance. Defaults to Depends(get_db).

  Returns:
      list[todo_schema.ToDo]: List of All todos in DB
  """
  todos = todo_crud.get_todos(db=db, skip=skip, limit=limit)
  return todos

@app.get('/todos/me/', response_model=list[todo_schema.ToDo])
def get_todos_for_user(current_user: Annotated[user_schema.User, Depends(user_crud.get_current_active_user)]) -> list[todo_schema.ToDo]:
  """Endpoint to get all todos

  Args:
      current_user (Annotated[user_schema.User, Depends): The user to grab the todos from. Resolves from token

  Returns:
      list[todo_schema.ToDo]: List of all todos owned by current_user
  """
  return current_user.todos
  
@app.post('/todos/', response_model=todo_schema.ToDo)
def add_todo_for_user(todo: todo_schema.ToDoCreate, current_user: Annotated[user_schema.User, Depends(user_crud.get_current_active_user)], db: Session = Depends(get_db) ) -> todo_schema.ToDo:
  """Endpoint to post a todo

  Args:
      todo (todo_schema.ToDoCreate): The todo to create
      current_user (Annotated[user_schema.User, Depends): The current user to post the todo to.
      db (Session, optional): DB Instance. Defaults to Depends(get_db).

  Raises:
      HTTPException: 400 - Raises if todo has an empty title
      HTTPException: 404 - Raises if cannot retrieve the user

  Returns:
      todo_schema.ToDo: The newly created todo.
  """
  if not todo.title:
    raise HTTPException(status_code=400, detail='Todo item cannot have an empty title.')
  if not current_user:
    raise HTTPException(status_code=404, detail="Cannot get user to add todo")
  
  return todo_crud.create_user_todo(db=db,todo=todo,user_id=current_user.id)

@app.post('/todos/{todo_id}/completed', response_model=todo_schema.ToDo)
def mark_todo_complete(todo_id: int, current_user: Annotated[user_schema.User, Depends(user_crud.get_current_active_user)], db: Session = Depends(get_db)) -> todo_schema.ToDo:
  """Endpoint to mark a todo complete.

  Args:
      todo_id (int): The id of todo to mark complete
      current_user (Annotated[user_schema.User, Depends): The authorized user
      db (Session, optional): DB Instance. Defaults to Depends(get_db).

  Raises:
      HTTPException: 400 - Raises if no todo_id is provided
      HTTPException: 404 - Raises if cannot retrieve the user

  Returns:
      todo_schema.ToDo: The updated todo with `is_complete = True`
  """
  if not todo_id:
    raise HTTPException(status_code=400, detail='Please provide the todo_id to update')
  if not current_user:
    raise HTTPException(status_code=404, detail="Cannot get user to add todo")
    

  return todo_crud.mark_complete(db=db, user_id=current_user.id, todo_id=todo_id)