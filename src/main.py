from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging

from .config.settings import settings
from .config.json_db import db
from .controllers import (
    auth_router,
    transaction_router,
    card_router,
    savings_router,
    reminder_router,
    dashboard_router
)
from .middleware.error_handler import (
    validation_exception_handler,
    general_exception_handler
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager para el ciclo de vida de la aplicación.
    Se ejecuta al inicio y al final de la aplicación.
    """
    # Startup
    logger.info("Starting Personal Finance API")
    logger.info(f"Data directory: {settings.DATA_DIR}")
    logger.info(
        f"JWT expires in: {settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes")

    # Inicializar la base de datos JSON
    db._ensure_data_dir()
    db._initialize_collections()
    logger.info("JSON Database initialized")

    yield

    # Shutdown
    logger.info("Shutting down Personal Finance API")


# Crear la aplicación FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="""
# API de Finanzas Personales

**Proyecto 2 - Diseño de Software**  
**Tecnológico de Costa Rica - Campus San Carlos**

**Desarrollado por:**
- Sebastián Josué Sandí Blanco
- Mario Andrés Rojas Varela

---
    """
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar manejadores de errores
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Registrar routers con prefijo /api/v1
API_PREFIX = f"/api/{settings.API_VERSION}"

app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(transaction_router, prefix=API_PREFIX)
app.include_router(card_router, prefix=API_PREFIX)
app.include_router(savings_router, prefix=API_PREFIX)
app.include_router(reminder_router, prefix=API_PREFIX)
app.include_router(dashboard_router, prefix=API_PREFIX)


@app.get("/")
async def root():
    """
    Endpoint raíz de la API.
    Retorna información básica sobre la API.
    """
    return {
        "message": "Personal Finance API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """
    Endpoint de health check para monitoreo.
    Útil para verificar que la API está funcionando correctamente.
    """
    return {
        "status": "healthy",
        "database": "connected",
        "timestamp": "2025-01-01T00:00:00Z"
    }


# Para ejecutar con uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
