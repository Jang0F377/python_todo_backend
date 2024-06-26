from pydantic import BaseModel
from typing import Union


class ToDoBase(BaseModel):
  title: str
  description: Union[str, None] = None
  is_complete: bool = False
  
class ToDoCreate(ToDoBase):
  pass


class ToDo(ToDoBase):
  id: int
  user_id: int
  
  class Config:
    orm_mode = True