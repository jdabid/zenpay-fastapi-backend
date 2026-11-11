from fastapi import APIRouter, status

router = APIRouter()

@router.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
def health_check():
    """Endpoint de verificación de estado y resiliencia del sistema."""
    return {
        "status": "healthy",
        "service": "ZenPay Backend API",
        "mensaje": "Servidor operando con resiliencia y paz mental 🍵✨"
    }
