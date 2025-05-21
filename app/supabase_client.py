#supabase_client.py
from app.database import supabase
from app.config import settings
from postgrest.exceptions import APIError # Import APIError


class SupabaseClient:
    def __init__(self):
        self.client = supabase
        self.bucket = settings.supabase_bucket
        self.storage = supabase.storage  # Add storage attribute

    def upload_video(self, filename: str, data: bytes):
        res = self.storage.from_(self.bucket).upload(filename, data)
        if res.get("error"):
            raise Exception(f"Supabase upload error: {res['error']}")
        return filename

    def get_signed_url(self, filename: str, expires_in: int = 3600):
        try:
            url_res = self.storage.from_(self.bucket).create_signed_url(filename, expires_in)
            if url_res and url_res.get("error"): # Check if url_res is dict and has error
                raise Exception(f"Supabase signed URL error: {url_res['error']}")
            return url_res.get("signedURL")
        except Exception as e: # Catch any exceptions raised by the storage client
            raise Exception(f"Supabase signed URL error: {e}")

    def insert_video_metadata(self, metadata: dict):
        res = self.client.table("videos").insert(metadata).execute()
        if res.get("error"):
            raise Exception(f"Supabase insert metadata error: {res['error']}")
        return res

    def get_videos_for_user(self, user_id: int):
        try:
            res = self.client.table("videos").select("*").eq("user_id", user_id).order("timestamp", desc=True).execute()
            # If execute() raises an APIError, it's caught by the caller in endpoints.py
            return res.data
        except APIError as e:
            raise Exception(f"Supabase get videos error: {e.message}")
        except Exception as e:
            raise Exception(f"An unexpected error occurred while fetching videos for user: {e}")

supabase_client = SupabaseClient()
