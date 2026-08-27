import os
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.database import get_db
from app.models.user import User
from app.schemas import LoginRequest, LoginResponse, ChangePasswordRequest, ResponseModel

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY", "nengtan-secret-key-change-in-production-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def create_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="无效的认证凭据")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token已过期或无效")
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在或已禁用")
    return user


@router.post("/login", response_model=ResponseModel)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not pwd_context.verify(req.password, user.password_hash):
        return ResponseModel(code=401, message="用户名或密码错误")
    if not user.is_active:
        return ResponseModel(code=403, message="账号已被禁用")
    token = create_token({"user_id": user.id, "username": user.username})
    return ResponseModel(data=LoginResponse(
        token=token, username=user.username, name=user.name
    ))


@router.get("/userinfo", response_model=ResponseModel)
def get_userinfo(current_user: User = Depends(get_current_user)):
    return ResponseModel(data={
        "id": current_user.id,
        "username": current_user.username,
        "name": current_user.name,
        "role": current_user.role,
    })


@router.post("/change-password", response_model=ResponseModel)
def change_password(
    req: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not pwd_context.verify(req.old_password, current_user.password_hash):
        return ResponseModel(code=400, message="原密码错误")
    current_user.password_hash = pwd_context.hash(req.new_password)
    db.commit()
    return ResponseModel(message="密码修改成功")
