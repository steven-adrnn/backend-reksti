from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.config import settings
from app.models import User
from passlib.context import CryptContext
from app.supabase_client import supabase_client

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Add the missing get_password_hash function
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def get_user(username: str) -> Optional[User]:
    res = supabase_client.client.table("users").select("*").eq("username", username).execute()
    
    # Fix: Use proper attribute access
    if hasattr(res, "error") and res.error or not hasattr(res, "data") or not res.data:
        return None
    
    user_data = res.data[0]
    
    # Handle different response types
    if isinstance(user_data, dict):
        return User(
            id=user_data.get("id"),
            username=user_data.get("username"),
            email=user_data.get("email")
        )
    else:
        return User(
            id=getattr(user_data, "id", None),
            username=getattr(user_data, "username", None),
            email=getattr(user_data, "email", None)
        )

def authenticate_user(username: str, password: str) -> Optional[User]:
    res = supabase_client.client.table("users").select("*").eq("username", username).execute()
    
    # Fix: Use proper attribute access
    if hasattr(res, "error") and res.error or not hasattr(res, "data") or not res.data:
        return None
    
    user_data = res.data[0]
    
    # Handle different response types and field names
    if isinstance(user_data, dict):
        # Check if we're using "password" or "hashed_password" field
        password_field = "password" if "password" in user_data else "hashed_password"
        
        if not verify_password(password, user_data[password_field]):
            return None
            
        return User(
            id=user_data.get("id"),
            username=user_data.get("username"),
            email=user_data.get("email")
        )
    else:
        # Check if we're using "password" or "hashed_password" field
        password_field = "password" if hasattr(user_data, "password") else "hashed_password"
        
        if not verify_password(password, getattr(user_data, password_field, None)):
            return None
            
        return User(
            id=getattr(user_data, "id", None),
            username=getattr(user_data, "username", None),
            email=getattr(user_data, "email", None)
        )

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user

def create_user(username, email, password):
    """
    Create a new user in the database with the provided username, email, and password.
    The password is hashed before storage.
    """
    # Use the newly added get_password_hash function
    hashed_password = get_password_hash(password)
    
    # Create user in Supabase
    res = supabase_client.client.table("users").insert({
        "username": username,
        "email": email,
        "password": hashed_password  # Make sure this field name matches your database schema
    }).execute()
    
    # Fix: Check attributes directly instead of using .get()
    if hasattr(res, "error") and res.error:
        return None
    
    # Check if data exists and has entries
    if not hasattr(res, "data") or not res.data or len(res.data) == 0:
        return None
    
    # Return the created user
    user_data = res.data[0]
    return User(
        id=user_data.get("id") if isinstance(user_data, dict) else getattr(user_data, "id", None),
        username=user_data.get("username") if isinstance(user_data, dict) else getattr(user_data, "username", None),
        email=user_data.get("email") if isinstance(user_data, dict) else getattr(user_data, "email", None)
    )