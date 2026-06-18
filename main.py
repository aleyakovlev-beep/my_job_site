from fastapi import FastAPI, Depends, Request, Form, Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import models
from database import engine, get_db

# Автоматически создаем файл базы данных jobs.db и таблицы в нем
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Указываем FastAPI, где искать HTML-шаблоны
templates = Jinja2Templates(directory="templates")

# Функция для наполнения базы тестовыми вакансиями, если она пустая
def create_test_vacancies(db: Session):
    if db.query(models.Vacancy).count() == 0:
        v1 = models.Vacancy(title="Python разработчик", company_name="АйтиПро", description="Писать код на FastAPI. Опыт от 1 года.", salary=120000, is_remote=True)
        v2 = models.Vacancy(title="Тестировщик QA", company_name="ТестЛаб", description="Искать баги в сайтах и мобильных приложениях.", salary=80000, is_remote=False)
        v3 = models.Vacancy(title="Фронтенд разработчик", company_name="ВебСтудия", description="Верстка красивых интерфейсов на React.", salary=100000, is_remote=True)
        db.add_all([v1, v2, v3])
        db.commit()

# 1. ГЛАВНАЯ СТРАНИЦА (теперь принимает опциональный email вошедшего пользователя)
@app.get("/")
def read_root(request: Request, user_email: str = None, db: Session = Depends(get_db)):
    create_test_vacancies(db)
    vacancies = db.query(models.Vacancy).all()
    # Передаем email на главную страницу, чтобы кнопки знали, кто авторизован
    return templates.TemplateResponse("index.html", {"request": request, "vacancies": vacancies, "user_email": user_email})

# 2. МАРШРУТ ДЛЯ ДОБАВЛЕНИЯ ВАКАНСИИ
@app.post("/add-vacancy")
def add_vacancy(
    title: str = Form(...),
    company_name: str = Form(...),
    description: str = Form(...),
    salary: int = Form(...),
    is_remote: bool = Form(False),
    user_email: str = Form(None),
    db: Session = Depends(get_db)
):
    new_vacancy = models.Vacancy(title=title, company_name=company_name, description=description, salary=salary, is_remote=is_remote)
    db.add(new_vacancy)
    db.commit()
    
    # Возвращаемся на главную и сохраняем авторизацию в адресе
    url = f"/?user_email={user_email}" if user_email else "/"
    return RedirectResponse(url=url, status_code=303)

# 3. МАРШРУТ ДЛЯ УДАЛЕНИЯ ВАКАНСИИ
@app.post("/delete-vacancy/{vacancy_id}")
def delete_vacancy(vacancy_id: int, user_email: str = Form(None), db: Session = Depends(get_db)):
    vacancy = db.query(models.Vacancy).filter(models.Vacancy.id == vacancy_id).first()
    if vacancy:
        db.delete(vacancy)
        db.commit()
    url = f"/?user_email={user_email}" if user_email else "/"
    return RedirectResponse(url=url, status_code=303)

# 4. СТРАНИЦА РЕГИСТРАЦИИ
@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
def register_user(email: str = Form(...), password: str = Form(...), role: str = Form(...), db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == email).first()
    if existing_user:
        return "Пользователь с таким email уже существует!"
    new_user = models.User(email=email, password=password, role=role)
    db.add(new_user)
    db.commit()
    return RedirectResponse(url="/login", status_code=303)

# 5. СТРАНИЦА ВХОДА
@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login_user(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email, models.User.password == password).first()
    if not user:
        return "Неверный email или пароль!"
    return RedirectResponse(url=f"/dashboard?user_email={email}", status_code=303)

# 6. СТРАНИЦА ЛИЧНОГО КАБИНЕТА
@app.get("/dashboard")
def dashboard_page(request: Request, user_email: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_email).first()
    if not user:
        return "Пользователь не найден"
    my_applications = db.query(models.Application).filter(models.Application.applicant_email == user_email).all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "applications": my_applications})

# 7. МАРШРУТ ДЛЯ ОТКЛИКА НА ВАКАНСИЮ
@app.post("/apply/{vacancy_id}")
def apply_to_vacancy(vacancy_id: int, user_email: str = Form(...), db: Session = Depends(get_db)):
    new_application = models.Application(vacancy_id=vacancy_id, applicant_email=user_email)
    db.add(new_application)
    db.commit()
    return RedirectResponse(url=f"/dashboard?user_email={user_email}", status_code=303)
    from fastapi import APIRouter, Response, status
from fastapi.responses import RedirectResponse

# Маршрут для выхода из аккаунта
@app.get("/logout")
async def logout():
    from fastapi import Response
    from fastapi.responses import RedirectResponse
    
    # Создаем ответ с перенаправлением на главную страницу
    response = RedirectResponse(url="/", status_code=303)
    
    # Удаляем куку авторизации. 
    # ВНИМАНИЕ: Если ваша кука называется по-другому (например, "session" или "token"),
    # замените "access_token" на ваше название.
    response.delete_cookie(key="access_token")
    
    return response

