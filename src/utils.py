from __future__ import annotations

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Iterable

try:
    from config import PATHS
except ImportError:
    PATHS = {
        "known_faces": "data/known_faces/",
        "unknown_faces": "data/unknown_faces/",
        "audit_logs": "data/audit_logs/",
    }


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def resolve_project_path(path: str | os.PathLike) -> Path:
    """Devuelve una ruta absoluta dentro del proyecto cuando recibe rutas relativas."""
    path_obj = Path(path)
    if path_obj.is_absolute():
        return path_obj
    return PROJECT_ROOT / path_obj


def ensure_directories(paths: Iterable[str | os.PathLike] | None = None) -> None:
    """Crea las carpetas necesarias para el sistema."""
    paths = paths or PATHS.values()
    for path in paths:
        resolve_project_path(path).mkdir(parents=True, exist_ok=True)


def iter_image_files(directory: str | os.PathLike) -> list[Path]:
    """Lista imagenes validas de una carpeta, ignorando archivos temporales."""
    folder = resolve_project_path(directory)
    if not folder.exists():
        return []

    return sorted(
        path
        for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )


def employee_code_from_image_path(image_path: str | os.PathLike) -> str:
    """
    Extrae el codigo de empleado desde el nombre de la imagen.

    Convenciones soportadas:
    - EMP001.jpg
    - EMP001_nombre_apellido.jpg
    - EMP001-nombre-apellido.jpg
    """
    stem = Path(image_path).stem.strip()
    parts = re.split(r"[_.\-\s]+", stem, maxsplit=1)
    return parts[0].upper()


def safe_filename(value: str) -> str:
    """Convierte texto libre en un nombre de archivo seguro."""
    clean = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip())
    return clean.strip("._") or "sin_nombre"


def timestamp_for_filename(moment: datetime | None = None) -> str:
    moment = moment or datetime.now()
    return moment.strftime("%Y%m%d_%H%M%S_%f")


def save_unknown_face(frame, location, output_dir: str | os.PathLike | None = None) -> Path | None:
    """
    Guarda una captura del rostro desconocido.

    `location` debe venir en formato face_recognition: (top, right, bottom, left).
    Retorna None si OpenCV no esta disponible o la imagen no se puede guardar.
    """
    try:
        import cv2
    except ImportError:
        return None

    output_dir = output_dir or PATHS["unknown_faces"]
    folder = resolve_project_path(output_dir)
    folder.mkdir(parents=True, exist_ok=True)

    top, right, bottom, left = location
    face_image = frame[max(top, 0) : max(bottom, 0), max(left, 0) : max(right, 0)]
    if face_image.size == 0:
        return None

    filename = f"desconocido_{timestamp_for_filename()}.jpg"
    output_path = folder / filename
    saved = cv2.imwrite(str(output_path), face_image)
    return output_path if saved else None
