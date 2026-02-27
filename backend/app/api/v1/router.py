from fastapi import APIRouter

from .blog.router import router as blog_router
from .media.router import router as media_router
# Import other routers as they are created
# from .admin.router import router as admin_router
# from .users.router import router as users_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(blog_router)
api_router.include_router(media_router)
# api_router.include_router(admin_router)
# api_router.include_router(users_router)
