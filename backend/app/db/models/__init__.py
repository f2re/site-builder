# Module: db/models/__init__.py | Agent: backend-agent | Task: phase3_backend_blog
# Import all models here so that Alembic autogenerate can discover them
# via Base.metadata when env.py imports this package.
from app.db.models.user import User          # noqa: F401
from app.db.models.order import Order        # noqa: F401
from app.db.models.user_device import UserDevice  # noqa: F401
from app.db.models.product import Category, Product, ProductVariant, ProductImage  # noqa: F401
from app.db.models.blog import BlogCategory, Tag, BlogPost  # noqa: F401
