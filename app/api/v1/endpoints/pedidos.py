from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.pedido import PedidoDB
from app.schemas.pedido import (
    PedidoCreate,
    PedidoResponse,
    DescuentoPromedioResponse
)

router = APIRouter()

@router.get("/", response_model=List[PedidoResponse], status_code=status.HTTP_200_OK)
def listar_pedidos(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """Lista todos los pedidos registrados en ZenPay."""
    return db.query(PedidoDB).offset(skip).limit(limit).all()

@router.post("/", response_model=PedidoResponse, status_code=status.HTTP_201_CREATED)
def crear_pedido(pedido_in: PedidoCreate, db: Session = Depends(get_db)):
    """Registra y cobra un nuevo pedido con validación estricta Pydantic."""
    nuevo_pedido = PedidoDB(
        cliente=pedido_in.cliente,
        plato=pedido_in.plato,
        monto=pedido_in.monto,
        cupones=pedido_in.cupones,
        estado="PAGADO"
    )
    db.add(nuevo_pedido)
    db.commit()
    db.refresh(nuevo_pedido)
    return nuevo_pedido

@router.get("/{pedido_id}", response_model=PedidoResponse, status_code=status.HTTP_200_OK)
def obtener_pedido(pedido_id: int, db: Session = Depends(get_db)):
    """Consulta un pedido por ID con control semántico de HTTP 404."""
    pedido = db.query(PedidoDB).filter(PedidoDB.id == pedido_id).first()
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El pedido #{pedido_id} no existe en nuestro sistema."
        )
    return pedido

@router.get("/{pedido_id}/descuento-promedio", response_model=DescuentoPromedioResponse)
def calcular_descuento_promedio(pedido_id: int, db: Session = Depends(get_db)):
    """
    Calcula el descuento promedio por cupón blindado contra ZeroDivisionError.
    Devuelve 400 Bad Request si no tiene cupones en lugar de un error 500.
    """
    pedido = db.query(PedidoDB).filter(PedidoDB.id == pedido_id).first()
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El pedido #{pedido_id} no existe."
        )

    # 🛡️ Blindaje defensivo contra división por cero
    if pedido.cupones <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este pedido no tiene cupones aplicados para promediar."
        )

    promedio = round(pedido.monto / pedido.cupones, 2)
    return {
        "pedido_id": pedido.id,
        "cliente": pedido.cliente,
        "total": pedido.monto,
        "cupones": pedido.cupones,
        "descuento_promedio": promedio,
        "mensaje": "Cálculo realizado de forma segura sin colapsar el backend 🚀"
    }

@router.get("/simular/error-inesperado", tags=["Resiliencia"])
def simular_fallo_imprevisto():
    """Endpoint de auditoría técnica que simula un fallo no previsto para probar el Escudo Global."""
    return {"resultado": 1 / 0}
