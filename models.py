from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from database import Base

Base = declarative_base()

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=False)
    birthday = Column(Date, nullable=False)
    extra_data = Column(String, nullable=True)  # Убедитесь, что это поле добавлено

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
