from fastapi import APIRouter

from .auth.router import router as auth_router
from .users.router import router as users_router
from .products.router import router as products_router
from .blog.router import router as blog_router
from .media.router import router as media_router
from .cart.router import router as cart_router
from .orders.router import router as orders_router
from .payments.router import router as payments_router
from .delivery.router import router as delivery_router
from .iot.router import router as iot_router
from .pages.router import router as pages_router
from .firmware.router import router as firmware_router
from .admin.router import router as admin_router

api_router = APIRouter(prefix="/api/v1")

# Order matters for some route matching, but generally alphabetical or logical
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(products_router)
api_router.include_router(blog_router)
api_router.include_router(media_router)
api_router.include_router(cart_router)
api_router.include_router(orders_router)
api_router.include_router(payments_router)
api_router.include_router(delivery_router)
api_router.include_router(iot_router)
api_router.include_router(pages_router)
api_router.include_router(firmware_router)
api_router.include_router(admin_router)
