from datetime import datetime, timedelta

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import Settings
from app.models.entities import User
from app.schemas.trading import UserCreate


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, db: AsyncSession, settings: Settings):
        self.db = db
        self.settings = settings

    async def create_user(self, payload: UserCreate) -> User:
        user = User(email=str(payload.email), hashed_password=pwd_context.hash(payload.password))
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def authenticate(self, email: str, password: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user or not pwd_context.verify(password, user.hashed_password):
            return None
        return user

    def create_access_token(self, user: User) -> str:
        expires = datetime.utcnow() + timedelta(minutes=self.settings.access_token_expire_minutes)
        payload = {"sub": user.id, "email": user.email, "role": user.role, "exp": expires}
        return jwt.encode(payload, self.settings.jwt_secret.get_secret_value(), algorithm=self.settings.jwt_algorithm)
