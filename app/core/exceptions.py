import logging
import uuid
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("ZenPayAPI")

def setup_exception_handlers(app: FastAPI) -> None:
    """Configura los escudos globales defensivos contra fallos imprevistos."""

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Manejo controlado de excepciones HTTP semánticas (400, 404, etc.)."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "codigo": exc.status_code,
                "mensaje": exc.detail,
                "ruta": request.url.path
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Manejo de errores de validación de esquemas Pydantic (HTTP 422)."""
        errores = [{"campo": err["loc"][-1], "error": err["msg"]} for err in exc.errors()]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "status": "error",
                "mensaje": "Datos de entrada inválidos según las reglas de negocio.",
                "errores": errores
            }
        )

    @app.exception_handler(Exception)
    async def global_unhandled_exception_handler(request: Request, exc: Exception):
        """
        ESCUDO GLOBAL: Atrapa cualquier error 500 imprevisto (ej. ZeroDivisionError, KeyError).
        Evita que el hilo de Uvicorn colapse y protege la privacidad del servidor.
        """
        error_id = str(uuid.uuid4())[:8]
        logger.error(
            f"[ERROR_ID: {error_id}] Fallo imprevisto en {request.method} {request.url.path}: {exc}",
            exc_info=True
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "mensaje": "Ocurrió un error inesperado en el servidor. El sistema sigue activo manteniendo la paz.",
                "error_id": error_id,
                "soporte": "Indica este error_id a nuestro equipo de soporte técnico para atenderte de inmediato."
            }
        )
