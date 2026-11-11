from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class PedidoBase(BaseModel):
    cliente: str = Field(..., min_length=3, max_length=100, description="Nombre del cliente")
    plato: str = Field(..., min_length=3, max_length=100, description="Concepto o producto")
    monto: float = Field(..., gt=0.0, description="Monto total del pedido en USD")
    cupones: int = Field(default=0, ge=0, description="Cantidad de cupones aplicados")

class PedidoCreate(PedidoBase):
    pass

class PedidoResponse(PedidoBase):
    id: int
    estado: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DescuentoPromedioResponse(BaseModel):
    pedido_id: int
    cliente: str
    total: float
    cupones: int
    descuento_promedio: float
    mensaje: str
