from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime
from app.database.connection import Base

def utc_now():
    return datetime.now(timezone.utc)

class PedidoDB(Base):
    """Modelo ORM de persistencia para órdenes y pagos en ZenPay."""
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cliente = Column(String(100), nullable=False, index=True)
    plato = Column(String(100), nullable=False)
    monto = Column(Float, nullable=False)
    cupones = Column(Integer, default=0, nullable=False)
    estado = Column(String(50), default="PAGADO", nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
