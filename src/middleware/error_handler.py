from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Manejador personalizado para errores de validación de Pydantic.
    """
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": exc.errors()
        }
    )


async def integrity_exception_handler(request: Request, exc: IntegrityError):
    """
    Manejador para errores de integridad de la base de datos.
    """
    logger.error(f"Integrity error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "detail": "Database integrity error",
            "message": "The operation conflicts with existing data. This might be a duplicate entry."
        }
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """
    Manejador general para errores de SQLAlchemy.
    """
    logger.error(f"Database error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Database error",
            "message": "An error occurred while processing the database operation."
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """
    Manejador general para excepciones no capturadas.
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "message": "An unexpected error occurred. Please try again later."
        }
    )