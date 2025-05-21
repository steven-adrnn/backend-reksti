from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# User model for authentication
class User(BaseModel):
    id: int
    username: str
    email: str

# User login request
class UserLoginRequest(BaseModel):
    username: str
    password: str

# User login response with JWT token
class UserLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
class UserRegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

# Video metadata model
class VideoMetadata(BaseModel):
    id: int
    user_id: int
    video_url: str
    timestamp: datetime
    location: Optional[str] = None
