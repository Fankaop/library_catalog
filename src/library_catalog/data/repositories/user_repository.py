from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.user import User, UserRole

class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    
    async def get_by_email(self, email:str) -> User | None:
        result = await self.session.execute(select(User).where(User.email==email))
        return result.scalar_one_or_none()
    
    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.user_id==user_id))
        return result.scalar_one_or_none()
    
    async def create(self, email:str, username:str, hashed_password:str, role=UserRole.user) -> User:
        user = User(email=email, username=username, hashed_password=hashed_password, role=role)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user