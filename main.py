import tkinter as tk
from datetime import datetime

import cv2

from src.database import DatabaseManager
from src.detector import FaceRecognitionEngine
from src.gui import AccessControlGUI


LOG_REFRESH_MS = 2000
VIDEO_REFRESH_MS = 10
DETECTION_EVERY_N_FRAMES = 5


def format_access_logs(records):
    logs = []
    for record in records:
        fecha_hora = record.get("fecha_hora")
        if isinstance(fecha_hora, datetime):
            fecha_hora = fecha_hora.strftime("%H:%M:%S")

        nombre = record.get("nombre_descifrado") or record.get("motivo") or "N/A"
        logs.append(
            (
                record.get("registro_accesos_id", ""),
                nombre,
                fecha_hora or "",
                record.get("estado_acceso", ""),
            )
        )
    return logs


class AccessControlApp:
    def __init__(self, root):
        self.root = root
        self.gui = AccessControlGUI(root)
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.db = DatabaseManager()
        self.db_connected = self.db.connect()
        self.detector = None
        self.frame_counter = 0
        self.last_processed_frame = None

        if self.db_connected:
            self.db.crear_tablas()

        try:
            self.detector = FaceRecognitionEngine(db_manager=self.db if self.db_connected else None)
            print(f"Rostros cargados: {self.detector.known_codes}")
        except RuntimeError as error:
            print(f"No se pudo iniciar el motor facial: {error}")

        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def start(self):
        self.update_video()
        self.update_logs()

    def update_video(self):
        ret, frame = self.cap.read()

        if ret:
            processed_frame = frame
            self.frame_counter += 1

            should_detect = self.frame_counter % DETECTION_EVERY_N_FRAMES == 0
            if self.detector is not None and should_detect:
                try:
                    processed_frame, _ = self.detector.process_frame(frame)
                    self.last_processed_frame = processed_frame
                except Exception as error:
                    print(f"Error procesando frame: {error}")
            elif self.last_processed_frame is not None:
                processed_frame = frame

            self.gui.update_video_frame(processed_frame)

        self.root.after(VIDEO_REFRESH_MS, self.update_video)

    def update_logs(self):
        if self.db_connected:
            records = self.db.obtener_ultimos_registros(10)
            self.gui.update_logs(format_access_logs(records))

        self.root.after(LOG_REFRESH_MS, self.update_logs)

    def close(self):
        if self.cap.isOpened():
            self.cap.release()
        if self.db_connected:
            self.db.disconnect()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = AccessControlApp(root)
    app.start()
    root.mainloop()
