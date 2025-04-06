from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from app.models.post import PostStatus

# Shared properties
class PostBase(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    hashtags: Optional[List[str]] = None
    status: Optional[PostStatus] = PostStatus.DRAFT
    scheduled_for: Optional[datetime] = None

# Properties to receive via API on creation
class PostCreate(PostBase):
    title: str
    content: str

# Properties to receive via API on update
class PostUpdate(PostBase):
    pass

# Properties shared by models stored in DB
class PostInDBBase(PostBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# Additional properties to return via API
class Post(PostInDBBase):
    pass

# Response model for API
class PostResponse(Post):
    pass

# Additional properties stored in DB
class PostInDB(PostInDBBase):
    pass 