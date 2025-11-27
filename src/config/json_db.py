import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
from .settings import settings
import logging

logger = logging.getLogger(__name__)


class JSONDatabase:
    """
    Clase para manejar archivos JSON como base de datos.
    Cada colección es un archivo JSON separado.
    """

    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir or settings.DATA_DIR)
        self._ensure_data_dir()
        self._initialize_collections()

    def _ensure_data_dir(self):
        """Asegura que el directorio de datos existe"""
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Data directory ready: {self.data_dir}")
        except PermissionError as e:
            logger.warning(f"Permission error creating {self.data_dir}: {e}")
            # Fallback to /tmp for Azure/restricted environments
            self.data_dir = Path("/tmp/finance_data")
            self.data_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Using fallback data directory: {self.data_dir}")
        except Exception as e:
            logger.error(f"Error creating data directory: {e}")
            # Last resort fallback
            self.data_dir = Path("/tmp/finance_data")
            self.data_dir.mkdir(parents=True, exist_ok=True)
            logger.warning(f"Using emergency fallback: {self.data_dir}")

    def _initialize_collections(self):
        """Inicializa los archivos JSON para cada colección si no existen"""
        collections = [
            "users",
            "transactions",
            "cards",
            "savings_envelopes",
            "payment_reminders"
        ]

        for collection in collections:
            try:
                file_path = self.data_dir / f"{collection}.json"
                if not file_path.exists():
                    self._write_json(file_path, [])
                    logger.info(f"Initialized collection: {collection}")
            except Exception as e:
                logger.error(
                    f"Error initializing collection {collection}: {e}")

    def _read_json(self, file_path: Path) -> List[Dict[str, Any]]:
        """Lee un archivo JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _write_json(self, file_path: Path, data: List[Dict[str, Any]]):
        """Escribe datos en un archivo JSON"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    def _get_collection_path(self, collection: str) -> Path:
        """Obtiene la ruta del archivo de una colección"""
        return self.data_dir / f"{collection}.json"

    def _get_next_id(self, collection: str) -> int:
        """Obtiene el siguiente ID disponible para una colección"""
        data = self.read_all(collection)
        if not data:
            return 1
        return max(item.get('id', 0) for item in data) + 1

    def read_all(self, collection: str) -> List[Dict[str, Any]]:
        """Lee todos los registros de una colección"""
        file_path = self._get_collection_path(collection)
        return self._read_json(file_path)

    def read_by_id(self, collection: str, id: int) -> Optional[Dict[str, Any]]:
        """Lee un registro por su ID"""
        data = self.read_all(collection)
        for item in data:
            if item.get('id') == id:
                return item
        return None

    def read_by_field(self, collection: str, field: str, value: Any) -> List[Dict[str, Any]]:
        """Lee registros que coincidan con un campo específico"""
        data = self.read_all(collection)
        return [item for item in data if item.get(field) == value]

    def create(self, collection: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un nuevo registro"""
        all_data = self.read_all(collection)

        # Asignar ID
        data['id'] = self._get_next_id(collection)

        # Agregar timestamps
        now = datetime.utcnow().isoformat()
        data['created_at'] = now
        data['updated_at'] = now

        all_data.append(data)
        file_path = self._get_collection_path(collection)
        self._write_json(file_path, all_data)

        return data

    def update(self, collection: str, id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Actualiza un registro existente"""
        all_data = self.read_all(collection)

        for i, item in enumerate(all_data):
            if item.get('id') == id:
                # Mantener ID y created_at
                data['id'] = id
                data['created_at'] = item.get('created_at')
                data['updated_at'] = datetime.utcnow().isoformat()

                all_data[i] = data
                file_path = self._get_collection_path(collection)
                self._write_json(file_path, all_data)

                return data

        return None

    def delete(self, collection: str, id: int) -> bool:
        """Elimina un registro por su ID"""
        all_data = self.read_all(collection)
        initial_length = len(all_data)

        all_data = [item for item in all_data if item.get('id') != id]

        if len(all_data) < initial_length:
            file_path = self._get_collection_path(collection)
            self._write_json(file_path, all_data)
            return True

        return False

    def find_one(self, collection: str, **filters) -> Optional[Dict[str, Any]]:
        """Encuentra un registro que coincida con los filtros"""
        data = self.read_all(collection)
        for item in data:
            match = all(item.get(key) == value for key,
                        value in filters.items())
            if match:
                return item
        return None

    def find_many(self, collection: str, **filters) -> List[Dict[str, Any]]:
        """Encuentra todos los registros que coincidan con los filtros"""
        data = self.read_all(collection)
        results = []
        for item in data:
            match = all(item.get(key) == value for key,
                        value in filters.items())
            if match:
                results.append(item)
        return results


# Instancia global de la base de datos
db = JSONDatabase()


def get_db() -> JSONDatabase:
    """
    Dependency para obtener la instancia de la base de datos JSON.
    Se usa en los controllers de FastAPI como dependency injection.
    """
    return db
