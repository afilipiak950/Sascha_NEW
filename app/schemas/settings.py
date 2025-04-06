from typing import Optional, List, Dict
from pydantic import BaseModel

# Shared properties
class SettingsBase(BaseModel):
    post_frequency: Optional[int] = 3
    daily_connection_limit: Optional[int] = 39
    interaction_interval: Optional[int] = 60
    auto_publish_posts: Optional[bool] = False
    auto_approve_comments: Optional[bool] = False
    target_industries: Optional[List[str]] = None
    target_locations: Optional[List[str]] = None
    target_company_sizes: Optional[List[str]] = None
    target_positions: Optional[List[str]] = None
    target_seniority: Optional[List[str]] = None
    target_keywords: Optional[List[str]] = None
    excluded_keywords: Optional[List[str]] = None
    interaction_types: Optional[List[str]] = None
    post_topics: Optional[List[str]] = None
    post_tones: Optional[List[str]] = None
    post_lengths: Optional[List[str]] = None
    post_hashtags: Optional[List[str]] = None
    message_templates: Optional[Dict[str, str]] = None
    notification_settings: Optional[Dict[str, bool]] = None
    proxy_settings: Optional[Dict[str, str]] = None
    browser_settings: Optional[Dict[str, str]] = None
    rate_limits: Optional[Dict[str, int]] = None

# Properties to receive via API on creation
class SettingsCreate(SettingsBase):
    pass

# Properties to receive via API on update
class SettingsUpdate(SettingsBase):
    pass

# Properties shared by models stored in DB
class SettingsInDBBase(SettingsBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

# Additional properties to return via API
class Settings(SettingsInDBBase):
    pass

# Additional properties stored in DB
class SettingsInDB(SettingsInDBBase):
    pass 