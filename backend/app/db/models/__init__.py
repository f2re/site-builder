# Module: db/models/__init__.py | Agent: backend-agent | Task: stage3_wiring
# Import all models here so that Alembic autogenerate can discover them
# via Base.metadata when env.py imports this package.
from app.db.models.user import User          # noqa: F401
from app.db.models.order import Order        # noqa: F401
from app.db.models.user_device import UserDevice  # noqa: F401
