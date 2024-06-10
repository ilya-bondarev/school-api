from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean, Text, TIMESTAMP, DECIMAL, TIME, CheckConstraint
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from config import Config

Base = declarative_base()
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)



class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    password = Column(String(255), nullable=False)
    login = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    photo = Column(Text)
    registration_date = Column(TIMESTAMP, default=datetime.now)
    description = Column(Text)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    role = relationship("Role", backref=backref("users", cascade="all, delete-orphan"))

class Status(Base):
    __tablename__ = 'statuses'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)

class Class(Base):
    __tablename__ = 'classes'
    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey('users.id'))
    student_id = Column(Integer, ForeignKey('users.id'))
    date_time = Column(TIMESTAMP, nullable=False)
    duration = Column(Integer, nullable=False)
    status_id = Column(Integer, ForeignKey('statuses.id'))
    status = relationship("Status", backref=backref("classes", cascade="all, delete-orphan"))

class LessonBoard(Base):
    __tablename__ = 'lesson_boards'
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    link = Column(Text, nullable=False)
