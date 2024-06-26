from pydantic import BaseModel
from .todo_schema import ToDo


class UserBase(BaseModel):
  username: str
  
  
class UserCreate(UserBase):
  password: str
  
class User(UserBase):
  id: int
  todos: list[ToDo]
  
  class Config:
    orm_mode = True