# Module: api/v1/router.py | Agent: backend-agent | Task: stage3_wiring
from fastapi import APIRouter

from app.api.v1.auth.router import router as auth_router
from app.api.v1.admin.router import router as admin_router
from app.api.v1.users.router import router as users_router
from app.api.v1.products.router import router as products_router

api_router = APIRouter()

# ── Public: Catalog ──────────────────────────────────────────────────────────
api_router.include_router(products_router)

# ── Public: authentication (register / login / refresh) ──────────────────────
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])

# ── Admin panel  (role=admin | is_superuser)  ─────────────────────────────────
#    All routes under /api/v1/admin/...
#    Protected globally by require_admin dependency inside admin/router.py
api_router.include_router(admin_router)  # prefix="/admin" already set in router

# ── User cabinet (any authenticated user) ────────────────────────────────────
#    All routes under /api/v1/users/...
#    Protected globally by require_customer dependency inside users/router.py
api_router.include_router(users_router)  # prefix="/users" already set in router
