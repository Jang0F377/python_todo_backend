from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..models.todo_model import ToDo
from ..schemas import todo_schema

def get_todos(db: Session, skip: int = 0, limit: int = 100) -> list[todo_schema.ToDo]:
  """CRUD function to query and return ALL todos in DB.

  Args:
      db (Session): DB Instance
      skip (int, optional): Offset to apply to the returned query. Defaults to 0.
      limit (int, optional): Limit on how many items to return. Defaults to 100.

  Returns:
      list[todo_schema.ToDo]: List of ALL todos in DB
  """
  return db.query(ToDo).offset(skip).limit(limit).all()

def create_user_todo(db: Session, todo: todo_schema.ToDoCreate, user_id: int) -> todo_schema.ToDo:
  """CRUD function to post a new todo for the current_user

  Args:
      db (Session): DB Instance
      todo (todo_schema.ToDoCreate): The todo to be created
      user_id (int): The owning user's id

  Returns:
      todo_schema.ToDo: The newly created Todo
  """
  todo_item = ToDo(**todo.model_dump(), user_id=user_id)
  db.add(todo_item)
  db.commit()
  db.refresh(todo_item)
  return todo_item

def mark_complete(db: Session,  user_id: int, todo_id: int) -> todo_schema.ToDo:
  """CRUD function to handle marking todo's as completed

  Args:
      db (Session): DB Instance
      user_id (int): The owning user's id
      todo_id (int): The id of the todo

  Raises:
      HTTPException: 404 - Raises if todo is not found by todo_id
      HTTPException: 403 - Raises if the todo_id is not owned by the user_id
      HTTPException: 400 - Raises if todo is already marked complete

  Returns:
      todo_schema.ToDo: The finished todo
  """
  todo = db.query(ToDo).filter(ToDo.id == todo_id).first()
  
  
  if not todo:
    raise HTTPException(status_code=404, detail="Todo not found by id")
  
  if todo.user_id is not user_id:
    raise HTTPException(status_code=403, detail="Not authorized to update that todo")
  
  if todo.is_complete is True:
    raise HTTPException(status_code=400, detail="Cannot edit a todo that is marked complete.")

  todo.is_complete = True
  db.commit()
  db.refresh(todo)
  return todo