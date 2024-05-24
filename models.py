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

class Language(Base):
    __tablename__ = 'languages'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    code = Column(String(3), unique=True, nullable=False)
    is_on_platform = Column(Boolean, nullable=False)

class Certificate(Base):
    __tablename__ = 'certificates'
    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    link = Column(Text, nullable=False)

class ProfileVideo(Base):
    __tablename__ = 'profile_videos'
    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    link = Column(Text, nullable=False)

class Review(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey('users.id'))
    student_id = Column(Integer, ForeignKey('users.id'))
    language_id = Column(Integer, ForeignKey('languages.id'))
    rating = Column(Integer, CheckConstraint('rating >= 1 AND rating <= 5'))
    comment = Column(Text)

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

class LessonHistory(Base):
    __tablename__ = 'lesson_history'
    id = Column(Integer, primary_key=True)
    lesson_id = Column(Integer)
    teacher_comment = Column(Text)
    student_assessment = Column(Integer, CheckConstraint('student_assessment >= 1 AND student_assessment <= 5'))
    student_wishes = Column(Text)
    lesson_board_id = Column(Integer, ForeignKey('lesson_boards.id'))
    lesson_board = relationship("LessonBoard", backref=backref("lesson_histories", cascade="all, delete-orphan"))

#TODO: Реализовать реферальную систему и расписание
class ReferralType(Base):
    __tablename__ = 'referral_types'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    bonus_amount = Column(DECIMAL(10,2), nullable=False)
    bonus_type = Column(String(255), nullable=False)
    condition_size = Column(DECIMAL(10,2), nullable=False)
    condition_type = Column(String(255), nullable=False)

class InvitationCode(Base):
    __tablename__ = 'invitation_codes'
    id = Column(Integer, primary_key=True)
    link = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)

class Referral(Base):
    __tablename__ = 'referrals'
    id = Column(Integer, primary_key=True) # InvitationCode id
    invited_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    referral_type_id = Column(Integer, ForeignKey('referral_types.id'), nullable=False)
    condition_fulfillment_date = Column(TIMESTAMP)
    status = Column(String(255), nullable=False)

class PromoCode(Base):
    __tablename__ = 'promo_codes'
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    promo_code_type = Column(String(255), nullable=False)
    discount = Column(DECIMAL(10,2), nullable=False)
    payout_amount = Column(DECIMAL(10,2))
    number_of_lessons = Column(Integer)

