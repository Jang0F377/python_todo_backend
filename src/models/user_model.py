from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base

class User(Base):
  """User Base Class

  Args:
      Base (_type_): inherits from declarative_base()
  """
  __tablename__ = 'users'
  
  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
  username: Mapped[str] = mapped_column(String(15), unique=True, index=True)
  hashed_password: Mapped[str]
  todos: Mapped[list['ToDo']] = relationship(back_populates='user', cascade="all, delete-orphan")
  
  