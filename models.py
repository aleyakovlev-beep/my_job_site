from sqlalchemy import Column, Integer, String, Boolean
from database import Base

# Описываем, как будет выглядеть таблица вакансий в базе данных
class Vacancy(Base):
    __tablename__ = "vacancies"

    id = Column(Integer, primary_key=True, index=True) # ID вакансии
    title = Column(String)                             # Название (например, Программист)
    company_name = Column(String)                      # Название компании
    description = Column(String)                       # Описание работы
    salary = Column(Integer)                           # Зарплата
    is_remote = Column(Boolean, default=False)         # Удаленка (Да/Нет)
# Новая таблица для пользователей сайта
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True) # Логин (почта)
    password = Column(String)                        # Пароль (в учебных целях храним строкой)
    role = Column(String)                            # Роль: 'applicant' (соискатель) или 'employer' (работодатель)
# Таблица для хранения откликов соискателей на вакансии
class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    vacancy_id = Column(Integer)  # ID вакансии, на которую откликнулись
    applicant_email = Column(String)  # Email студента, который откликнулся
