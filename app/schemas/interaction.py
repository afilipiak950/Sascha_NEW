from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.models.interaction import InteractionType, InteractionStatus

# Shared properties
class InteractionBase(BaseModel):
    type: Optional[InteractionType] = None
    status: Optional[InteractionStatus] = InteractionStatus.PENDING
    target_id: Optional[str] = None
    target_name: Optional[str] = None
    target_title: Optional[str] = None
    content: Optional[str] = None
    post_id: Optional[int] = None

# Properties to receive via API on creation
class InteractionCreate(InteractionBase):
    type: InteractionType
    target_id: str
    target_name: str
    target_title: str

# Properties to receive via API on update
class InteractionUpdate(InteractionBase):
    pass

# Properties shared by models stored in DB
class InteractionInDBBase(InteractionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Additional properties to return via API
class Interaction(InteractionInDBBase):
    pass

# Additional properties stored in DB
class InteractionInDB(InteractionInDBBase):
    pass 