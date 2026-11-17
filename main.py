from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, Session
from pydantic import BaseModel

DATABASE_URL = "postgresql://postgres.glzwofbvgjzbaiqwpgrn:yscmZQkl5OlqQHqI@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres"

engine = create_engine(DATABASE_URL)
Base = declarative_base()

# 테이블 모델(테이블 이름을 users)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(120))

class UserCreate(BaseModel):
    username: str
    email: str

# 테이블이 없으면 생성
Base.metadata.create_all(bind=engine)

# 요청마다 세션을 열고, 끝나면 닫는 함수
def get_db():
    db = Session(bind=engine)
    try: 
        yield db
    finally:
        db.close()

app = FastAPI()

# C:Create 회원가입
@app.post("/users")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(username=user.username, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "ok": "true",
        "id": new_user.id, 
        "username": new_user.username,
        "email": new_user.email
    }

# R:Read 가입한 정보 불러오기(전체조회)
@app.get("/users")
def read_users(db: Session=Depends(get_db)):
    users = db.query(User).all()
    return [
        {
            "id": user.id, 
            "username": user.username, 
            "email": user.email
        } for user in users
    ]

# R:Read 하나 조회
@app.get("/users/{user_id}")
def read_user(user_id: int, db: Session=Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None: 
        return HTTPException(status_code=404, deatal="사용자가 없습니다.")
    return {
        "id": user.id, 
        "username" : user.username, 
        "email": user.email
    }

# U:Update => 수정
@app.put("/users/{user_id}")
def update_user(user_id: int, data: UserCreate,  db: Session=Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None: 
        return HTTPException(status_code=404, deatal="사용자가 없습니다.")

    user.username = data.username
    user.email = data.email

    db.commit()
    db.refresh(user)
    
    return {
        "id": user.id,
        "username": user.username, 
        "email": user.email
    }

@app.delete("/users/{user_id}")
def delete_user(user_id:int,  db: Session=Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        return HTTPException(status_code=404, deatal="사용자가 없습니다.")

    db.delete(user)
    db.commit()

    return {
        "message": "삭제완료"
    }

 
@app.get("/")
def read_home():
    return {
        "hello" : "world"
    }