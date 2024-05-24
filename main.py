import os
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List
from fastapi import FastAPI, Form, HTTPException, Depends, WebSocket, WebSocketDisconnect, status, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic_schemas import UserCreate, Token, RefreshTokenRequest, UserLogIn, UserProfile, Block, Teacher, LessonCreate, Lesson
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import func, or_, select
from jose import JWTError
from config import Config
import models
import auth

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Board:
    def __init__(self):
        self.connections: List[WebSocket] = []
        self.blocks: Dict[int, Block] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)
        await self.send_update_blocks()

    def disconnect(self, websocket: WebSocket):
        self.connections.remove(websocket)

    async def send_update_blocks(self):
        data = {"type": "update_blocks", "blocks": [block.dict() for block in self.blocks.values()]}
        await self.broadcast(data)

    async def broadcast(self, message: dict):
        disconnected_connections = []
        for connection in self.connections:
            try:
                await connection.send_json(message)
            except RuntimeError as e:
                print(f"Error sending message: {e}")
                disconnected_connections.append(connection)

        for connection in disconnected_connections:
            self.disconnect(connection)

    async def receive_block_update(self, block: Block):
        self.blocks[block.id] = block
        await self.send_update_blocks()

    async def delete_block(self, block_id: int):
        if block_id in self.blocks:
            del self.blocks[block_id]
            await self.send_update_blocks()

boards: Dict[int, Board] = {}

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=models.engine)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_token_response(username: str, expires_delta: timedelta):
    access_token_expires = datetime.now() + expires_delta
    access_token = auth.create_access_token(data={"sub": username}, expires_delta=expires_delta)
    refresh_token = auth.create_refresh_token(data={"sub": username})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires": access_token_expires
    }

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = auth.decode_token(token)
        if payload is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        user = db.query(models.User).filter(models.User.login == username).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        
        # Проверка истечения срока действия токена
        if datetime.fromtimestamp(payload["exp"]) < datetime.now():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
        
        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@app.post("/register", response_model=Token)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        login=user.login, 
        password=hashed_password, 
        full_name=user.full_name, 
        photo=user.photo, 
        description=user.description, 
        role_id=user.role_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return create_token_response(user.login, timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES))

@app.post("/update-profile")
async def update_profile(
    full_name: str = Form(...),
    description: str = Form(...),
    photo: str = Form(None), 
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_user.full_name = full_name
    current_user.description = description

    if photo:
        current_user.photo = photo

    db.commit()
    db.refresh(current_user)

    return {"message": "Profile updated successfully"}


@app.post("/token", response_model=Token)
def login_for_access_token(form_data: UserLogIn, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.login == form_data.login).first()
    if not user or not auth.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return create_token_response(user.login, timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES))

@app.post("/refresh", response_model=Token)
def refresh_access_token(refresh_request: RefreshTokenRequest, db: Session = Depends(get_db)):
    try:
        payload = auth.decode_token(refresh_request.refresh_token)
        if payload is None or payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        # Проверка истечения срока действия токена
        if datetime.fromtimestamp(payload["exp"]) < datetime.now():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token has expired")

        access_token_expires = timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth.create_access_token(data={"sub": username}, expires_delta=access_token_expires)
        expires = datetime.now() + access_token_expires
        return {
            "access_token": access_token,
            "refresh_token": refresh_request.refresh_token,  # Возвращаем тот же refresh token
            "token_type": "bearer",
            "expires": expires
        }
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


@app.get("/me", response_model=UserProfile)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return UserProfile(
        id=current_user.id,
        full_name=current_user.full_name,
        login=current_user.login,
        role_id=current_user.role_id,
        registration_date=current_user.registration_date,
        photo=current_user.photo,
        description=current_user.description
    )

@app.websocket("/ws/{board_id}")
async def websocket_endpoint(websocket: WebSocket, board_id: int):
    if board_id not in boards:
        boards[board_id] = Board()
    board = boards[board_id]
    await board.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get('type')
            block_data = data.get('data')
            if action in ['add_block', 'move_block', 'resize_block', 'update_content'] and block_data:
                try:
                    block = Block(**block_data)
                    await board.receive_block_update(block)
                except Exception as e:
                    print(f"Validation error: {e}")
            elif action == 'delete_block' and block_data:
                try:
                    block_id = block_data['id']
                    await board.delete_block(block_id)
                except Exception as e:
                    print(f"Error deleting block: {e}")
    except WebSocketDisconnect:
        board.disconnect(websocket)
    except Exception as e:
        print(f"Error: {e}")
        board.disconnect(websocket)

@app.get("/teachers", response_model=List[Teacher])
def read_teachers(db: Session = Depends(get_db)):
    subquery_review = db.query(
        models.Review.teacher_id,
        func.avg(models.Review.rating).label('average_rating')
    ).group_by(models.Review.teacher_id).subquery()

    subquery_lessons = db.query(
        models.LessonHistory.lesson_id,
        func.count(models.LessonHistory.lesson_id).label('lessons_count')
    ).group_by(models.LessonHistory.lesson_id).subquery()

    teachers = db.query(
        models.User.id,
        models.User.full_name,
        models.User.description,
        models.User.photo,
        models.User.registration_date,
        subquery_review.c.average_rating,
        subquery_lessons.c.lessons_count
    ).join(
        subquery_review, models.User.id == subquery_review.c.teacher_id, isouter=True
    ).join(
        subquery_lessons, models.User.id == subquery_lessons.c.lesson_id, isouter=True
    ).filter(
        models.User.role_id == 2
    ).all()

    result = [
        {
            'id': teacher.id,
            'full_name': teacher.full_name,
            'description': teacher.description,
            'photo': teacher.photo,
            'registration_date': teacher.registration_date,
            'rating': teacher.average_rating if teacher.average_rating else 0,
            'lessons_amount': teacher.lessons_count if teacher.lessons_count else 0,
        }
        for teacher in teachers
    ]

    return result

@app.post("/lessons/", response_model=int)
def create_lesson(lesson: LessonCreate, db: Session = Depends(get_db)):
    teacher = db.get(models.User, lesson.teacher_id)
    student = db.get(models.User, lesson.student_id)
    
    if not teacher or not student:
        raise HTTPException(status_code=404, detail="Teacher, student, or status not found")
    
    new_lesson = models.Class(
        teacher_id=lesson.teacher_id,
        student_id=lesson.student_id,
        date_time=lesson.date_time,
        duration=lesson.duration,
        status_id=lesson.status_id,
    )
    
    db.add(new_lesson)
    db.commit()
    db.refresh(new_lesson)
    
    return new_lesson.id

@app.get("/lessons/user/{user_id}", response_model=List[Lesson])
def read_lessons(user_id: int, db: Session = Depends(get_db)):
    #TODO: Добавить usernames в ответ чтобы улучшить восприятие
    lessons_query = db.query(
        models.Class
    ).filter(
        or_(models.Class.teacher_id == user_id, models.Class.student_id == user_id)
    ).order_by(
        models.Class.date_time.asc()
    )

    lessons = lessons_query.all()

    result = [
        {
            'id':lesson.id,
            'teacher_id':lesson.teacher_id,
            'student_id':lesson.student_id,
            'date_time':lesson.date_time,
            'duration':lesson.duration,
            'status_id':lesson.status_id,
        }
        for lesson in lessons
    ]

    return result

@app.post("/upload-profile-photo/")
async def upload_profile_photo(file: UploadFile = File(...)):
    valid_extensions = {"jpg", "jpeg", "png", "gif"}
    filename = file.filename
    file_extension = filename.split(".")[-1].lower()

    if file_extension not in valid_extensions:
        raise HTTPException(status_code=400, detail="Invalid file extension")
    new_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(Config.IMAGE_UPLOAD_DIR, new_filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    return JSONResponse(content={"filename": new_filename})

@app.get("/profile-photo/{filename}")
async def get_profile_photo(filename: str):
    file_path = os.path.join(Config.IMAGE_UPLOAD_DIR, filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)


@app.post("/upload-certificates/")
async def upload_certificates(file: UploadFile = File(...)):
    #TODO: Write data about this into db
    valid_extensions = {"jpg", "jpeg", "png", "pdf"}
    filename = file.filename
    file_extension = filename.split(".")[-1].lower()

    if file_extension not in valid_extensions:
        raise HTTPException(status_code=400, detail="Invalid file extension")
    new_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(Config.IMAGE_UPLOAD_DIR, new_filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    return {"filename": new_filename}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), current_user: models.User = Depends(get_current_user)):
    teacher_folder = Path(os.path.join(Config.FILES_UPLOAD_DIR, str(current_user.id)))
    teacher_folder.mkdir(parents=True, exist_ok=True)
    file_path = Path(os.path.join(teacher_folder, file.filename))
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    return {"filename": file.filename}

@app.get("/my-files", response_model=List[str])
async def list_my_files(current_user: models.User = Depends(get_current_user)):
    teacher_folder = Path(os.path.join(Config.FILES_UPLOAD_DIR, str(current_user.id)))
    if not teacher_folder.exists():
        return []

    files = [f.name for f in teacher_folder.iterdir() if f.is_file()]
    return files

@app.get("/files/{teacher_id}/{file_name}", response_class=FileResponse)
async def read_file(teacher_id: int, file_name: str):
    file_path = Path(os.path.join(Config.FILES_UPLOAD_DIR, str(teacher_id), file_name))
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    
    return FileResponse(file_path)