# Module: db/models/__init__.py | Agent: backend-agent | Task: BE-03
# Import all models here so that Alembic autogenerate can discover them
# via Base.metadata when env.py imports this package.
from app.db.models.user import User          # noqa: F401
from app.db.models.order import Order, OrderItem        # noqa: F401
from app.db.models.user_device import UserDevice  # noqa: F401
from app.db.models.product import Category, Product, ProductVariant, ProductImage  # noqa: F401
from app.db.models.blog import BlogCategory, Tag, BlogPost  # noqa: F401
from app.db.models.redirect import Redirect  # noqa: F401
from app.db.models.notification import NotificationLog, UserNotificationSettings  # noqa: F401
from app.db.models.page import StaticPage  # noqa: F401
from app.db.models.cart import Cart, CartItem  # noqa: F401
from app.db.models.migration import MigrationJob  # noqa: F401
