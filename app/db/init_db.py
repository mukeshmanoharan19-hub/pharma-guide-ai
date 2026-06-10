"""Database initialization helpers.

Schema is owned by Alembic migrations. Run::

    alembic upgrade head

``init_db`` remains only as a manual dev escape hatch (e.g. throwaway test
databases) and is intentionally NOT called on application startup.
"""

from app.db.database import engine, Base

# Import models so they are registered on Base.metadata before create_all.
from app.models.user import User  # noqa: F401
from app.models.medicine import Medicine  # noqa: F401
from app.models.chat_session import ChatSession  # noqa: F401
from app.models.chat_message import ChatMessage  # noqa: F401
from app.models.conversation_summary import ConversationSummary  # noqa: F401
from app.models.cart import Cart, CartItem  # noqa: F401
from app.models.order import Order, OrderItem  # noqa: F401
from app.models.routing_log import RoutingLog  # noqa: F401
from app.models.checkout_confirmation import CheckoutConfirmation  # noqa: F401


def init_db():
    """Create all tables directly. Prefer Alembic migrations in real envs."""
    Base.metadata.create_all(bind=engine)
