import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import setup_exception_handlers
from app.database.connection import Base, engine
from app.api.v1.api import api_router

# Configuración de logging profesional
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(name)s): %(message)s"
)
logger = logging.getLogger("ZenPayAPI")

# Creación de tablas de la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
    ## 🍵 ZenPay Backend API — Pasarela de Pedidos y Pagos Resiliente
    API construida con **FastAPI**, **Pydantic v2**, **SQLAlchemy** y blindada con arquitectura defensiva contra errores 500.

    - 🚀 **Endpoints Semánticos**: HTTP 200, 201, 400, 404, 422
    - 🛡️ **Escudo Global de Excepciones**: Trazabilidad con `error_id`
    - 🧪 **QA Automation**: Cobertura con Pytest y TestClient
    """,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de escudos defensivos de excepciones
setup_exception_handlers(app)

# Registro de rutas de API v1
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Root"])
def root():
    return {
        "status": "online",
        "mensaje": "Bienvenido a ZenPay API. Aprende a programar manteniendo la paz 🍵",
        "documentacion": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
