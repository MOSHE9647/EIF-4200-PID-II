from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

try:
    from config import PATHS
except ImportError:
    PATHS = {
        "known_faces": "data/known_faces/",
        "unknown_faces": "data/unknown_faces/",
    }

from src.utils import employee_code_from_image_path, iter_image_files, save_unknown_face
try:
    import winsound
except ImportError:
    winsound = None

from src.notification import send_security_alert


@dataclass
class FaceMatch:
    codigo_empleado: str | None
    nombre: str
    location: tuple[int, int, int, int]
    autorizado: bool
    distance: float | None = None
    empleado: dict[str, Any] | None = None
    evidence_path: Path | None = None


class FaceRecognitionEngine:
    """
    Motor de reconocimiento facial.

    Usa `face_recognition` para generar embeddings de rostros autorizados y
    consulta la base de datos cada vez que identifica un rostro conocido.
    """

    def __init__(
        self,
        known_faces_dir: str | Path | None = None,
        unknown_faces_dir: str | Path | None = None,
        db_manager: Any | None = None,
        tolerance: float = 0.5,
        detection_model: str = "hog",
        min_seconds_between_logs: int = 10,
        auto_load: bool = True,
    ) -> None:
        self.known_faces_dir = known_faces_dir or PATHS["known_faces"]
        self.unknown_faces_dir = unknown_faces_dir or PATHS["unknown_faces"]
        self.db_manager = db_manager
        self.tolerance = tolerance
        self.detection_model = detection_model
        self.min_log_interval = timedelta(seconds=min_seconds_between_logs)
        self.known_encodings: list[Any] = []
        self.known_codes: list[str] = []
        self.last_log_by_key: dict[str, datetime] = {}

        self.cv2 = None
        self.face_recognition = None
        self._load_dependencies()

        if auto_load:
            self.load_known_faces()

    def _load_dependencies(self) -> None:
        missing = []
        try:
            import cv2

            self.cv2 = cv2
        except ImportError:
            missing.append("opencv-python")

        try:
            import face_recognition

            self.face_recognition = face_recognition
        except ImportError:
            missing.append("face_recognition")

        if missing:
            paquetes = ", ".join(missing)
            raise RuntimeError(
                f"Faltan dependencias para reconocimiento facial: {paquetes}. "
                "Instalalas con `pip install opencv-python face_recognition`."
            )

    def load_known_faces(self) -> int:
        """Carga rostros autorizados desde `data/known_faces`."""
        self.known_encodings.clear()
        self.known_codes.clear()

        for image_path in iter_image_files(self.known_faces_dir):
            encoding = self._encode_first_face(image_path)
            if encoding is None:
                print(f"Sin rostro detectable en: {image_path}")
                continue

            self.known_encodings.append(encoding)
            self.known_codes.append(employee_code_from_image_path(image_path))

        return len(self.known_encodings)

    def _encode_first_face(self, image_path: str | Path):
        image = self._load_rgb_image(image_path)
        locations = self.face_recognition.face_locations(image, model=self.detection_model)
        if not locations:
            return None

        encodings = self.face_recognition.face_encodings(image, known_face_locations=locations)
        return encodings[0] if encodings else None

    def _load_rgb_image(self, image_path: str | Path):
        with Image.open(image_path) as image:
            rgb_image = image.convert("RGB")
            return np.asarray(rgb_image, dtype=np.uint8)

    def process_frame(self, frame_bgr):
        """
        Procesa un frame BGR de OpenCV.

        Retorna:
        - frame anotado con cajas verdes/rojas
        - lista de FaceMatch con el resultado de cada rostro
        """
        rgb_frame = self.cv2.cvtColor(frame_bgr, self.cv2.COLOR_BGR2RGB)
        locations = self.face_recognition.face_locations(rgb_frame, model=self.detection_model)
        encodings = self.face_recognition.face_encodings(rgb_frame, locations)

        matches: list[FaceMatch] = []
        for location, encoding in zip(locations, encodings):
            match = self._match_encoding(encoding, location, frame_bgr)
            matches.append(match)
            self._draw_match(frame_bgr, match)

        return frame_bgr, matches

    def _match_encoding(self, encoding, location, frame_bgr) -> FaceMatch:
        if not self.known_encodings:
            return self._unknown_match(location, frame_bgr, "Sin rostros cargados")

        distances = self.face_recognition.face_distance(self.known_encodings, encoding)
        best_index = int(distances.argmin())
        best_distance = float(distances[best_index])

        if best_distance > self.tolerance:
            return self._unknown_match(location, frame_bgr, "Desconocido", best_distance)

        codigo = self.known_codes[best_index]
        empleado = None
        autorizado = True
        nombre = codigo

        if self.db_manager is not None:
            empleado = self.db_manager.obtener_empleado_por_codigo(codigo)
            autorizado = empleado is not None
            nombre = empleado.get("nombre_descifrado", codigo) if empleado else "Acceso denegado"

            log_key = f"empleado:{codigo}"
            if self._should_log(log_key):
                estado = "AUTORIZADO" if autorizado else "NO_AUTORIZADO"
                motivo = None if autorizado else f"Codigo {codigo} no registrado en base de datos"
                empleado_id = empleado.get("empleado_id") if empleado else None
                self.db_manager.registrar_acceso(empleado_id, estado, motivo)
                self._remember_log(log_key)

        return FaceMatch(
            codigo_empleado=codigo,
            nombre=nombre,
            location=location,
            autorizado=autorizado,
            distance=best_distance,
            empleado=empleado,
        )

    def _unknown_match(
        self,
        location,
        frame_bgr,
        label: str = "Desconocido",
        distance: float | None = None,
    ) -> FaceMatch:
        evidence_path = None
        if self._should_log("unknown"):
            evidence_path = save_unknown_face(frame_bgr, location, self.unknown_faces_dir)
            if self.db_manager is not None:
                self.db_manager.registrar_acceso(None, "NO_AUTORIZADO", label)
            
            # Alerta Sonora (Windows)
            if winsound:
                # Frecuencia 1000Hz, duración 500ms
                winsound.Beep(1000, 500)
            
            # Notificación Crítica por Correo
            if evidence_path:
                send_security_alert(evidence_path, label)
                
            self._remember_log("unknown")

        return FaceMatch(
            codigo_empleado=None,
            nombre=label,
            location=location,
            autorizado=False,
            distance=distance,
            evidence_path=evidence_path,
        )

    def _should_log(self, key: str) -> bool:
        last_log = self.last_log_by_key.get(key)
        return last_log is None or datetime.now() - last_log >= self.min_log_interval

    def _remember_log(self, key: str) -> None:
        self.last_log_by_key[key] = datetime.now()

    def _draw_match(self, frame_bgr, match: FaceMatch) -> None:
        top, right, bottom, left = match.location
        color = (0, 180, 0) if match.autorizado else (0, 0, 255)
        label = match.nombre if match.autorizado else "NO AUTORIZADO"

        self.cv2.rectangle(frame_bgr, (left, top), (right, bottom), color, 2)
        self.cv2.rectangle(frame_bgr, (left, bottom - 28), (right, bottom), color, self.cv2.FILLED)
        self.cv2.putText(
            frame_bgr,
            label[:32],
            (left + 6, bottom - 8),
            self.cv2.FONT_HERSHEY_DUPLEX,
            0.55,
            (255, 255, 255),
            1,
        )

    def recognize_image(self, image_path: str | Path) -> list[FaceMatch]:
        """Metodo util para probar el motor con una imagen sin abrir la camara."""
        frame = self.cv2.imread(str(image_path))
        if frame is None:
            raise ValueError(f"No se pudo leer la imagen: {image_path}")
        _, matches = self.process_frame(frame)
        return matches
