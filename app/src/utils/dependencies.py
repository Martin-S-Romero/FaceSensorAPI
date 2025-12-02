from app.src.services.storage_service import StorageService
from app.src.services.face_censor_service import FaceCensorService


_storage_service = StorageService()
_face_censor_service = FaceCensorService()


def get_storage_service() -> StorageService:
    return _storage_service


def get_face_censor_service() -> FaceCensorService:
    return _face_censor_service
