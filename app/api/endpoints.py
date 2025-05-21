#endpoint.py
from fastapi import APIRouter, Depends, HTTPException, status
from app.models import UserLoginRequest, UserLoginResponse, VideoMetadata, UserRegisterRequest
from app.auth import authenticate_user, create_access_token, get_current_user, create_user
from app.supabase_client import supabase_client
from typing import List
from postgrest.exceptions import APIError 

router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserRegisterRequest):
    # Fix: Use the data property directly instead of get() method
    res = supabase_client.client.table("users").select("*").eq("username", user.username).execute()
    
    # Check if there was an error or if users with the same username already exist
    if hasattr(res, "error") and res.error or (hasattr(res, "data") and res.data and len(res.data) > 0):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    
    created_user = create_user(user.username, user.email, user.password)
    if not created_user:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User creation failed")
    
    return {"message": "User registered successfully"}

@router.post("/login", response_model=UserLoginResponse)
async def login(form_data: UserLoginRequest):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    
    access_token = create_access_token(data={"sub": user.username})
    return UserLoginResponse(access_token=access_token)

@router.get("/videos", response_model=List[VideoMetadata])
async def get_videos(current_user=Depends(get_current_user)):
    try:
        # Remove the 'if res.error' check as APIError will be raised directly on failure
        res = supabase_client.client.table("videos").select("*").eq("user_id", current_user.id).order("timestamp", desc=True).execute()
        videos = res.data # res.data will be an empty list if no videos are found
        return [VideoMetadata(**video) for video in videos]
    except APIError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch videos from database: {e.message}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred while fetching videos: {e}")

@router.get("/videos/{video_id}/signed_url")
async def get_signed_url(video_id: int, current_user=Depends(get_current_user)):
    try:
        res = supabase_client.client.table("videos").select("*").eq("user_id", current_user.id).eq("id", video_id).execute()
        
        # Check if video exists and belongs to the current user
        if not res.data or len(res.data) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
        
        video = res.data[0]
        filename = video["video_url"]
        
        # Generate signed URL for the file in your user_videos bucket
        signed_url = supabase_client.get_signed_url(filename)
        return {"signed_url": signed_url}
        
    except APIError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch video from database: {e.message}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred while getting signed URL: {e}")
