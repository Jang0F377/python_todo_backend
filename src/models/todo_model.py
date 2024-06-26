from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from ..database import Base


class ToDo(Base):
  """ToDo Base class

  Args:
      Base: inherits from declarative_base()
  """
  __tablename__ = 'todos'
  
  id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
  title: Mapped[str] = mapped_column(String(30))
  description: Mapped[Optional[str]]
  is_complete: Mapped[bool] = mapped_column(default=False)
  user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
  
  user: Mapped['User'] = relationship(back_populates='todos')