from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY

from dressup.models.base import Base


class Category(Base):
  __tablename__ = "categories"

  id = Column(Integer, primary_key=True)
  display_name = Column(String(32), unique=True)

  options = Column(ARRAY(String(32)))
