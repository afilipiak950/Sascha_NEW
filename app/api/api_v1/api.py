from fastapi import APIRouter

from app.api.api_v1.endpoints import posts, users, interactions, target_contacts, scheduler

api_router = APIRouter()

# Posts
api_router.include_router(
    posts.router,
    prefix="/posts",
    tags=["posts"]
)

# Users
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"]
)

# Interactions
api_router.include_router(
    interactions.router,
    prefix="/interactions",
    tags=["interactions"]
)

# Target Contacts
api_router.include_router(
    target_contacts.router,
    prefix="/target-contacts",
    tags=["target-contacts"]
)

# Scheduler
api_router.include_router(
    scheduler.router,
    prefix="/scheduler",
    tags=["scheduler"]
) 