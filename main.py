import tkinter as tk
import cv2
from src.gui import AccessControlGUI
# from detector import FaceDetector
# from database import DBManager

def video_loop():
    # 1. Capturar frame de la cámara
    ret, frame = cap.read()
    
    if ret:
        # 2. Aquí se llamaría a la lógica de reconocimiento facial (detector.py)
        # frame_procesado = detector.process_frame(frame) 
        # (Este frame procesado ya debería tener los cuadros delimitadores)
        
        # 3. Enviar el frame a la GUI
        app.update_video_frame(frame) # Reemplazar 'frame' por 'frame_procesado'

    # Repetir el ciclo cada 10 milisegundos para dar fluidez 
    root.after(10, video_loop)

if __name__ == "__main__":
    root = tk.Tk()
    app = AccessControlGUI(root)
    
    # Inicializar cámara
    cap = cv2.VideoCapture(0)
    
    # Iniciar el bucle de video
    video_loop()
    
    # Ejemplo de cómo inyectar datos falsos temporalmente para probar el panel
    app.update_logs([
        ("1", "Juan Pérez", "10:05:22", "Autorizado"),
        ("2", "Desconocido", "10:15:00", "Alerta")
    ])
    
    root.mainloop()
    
    # Liberar recursos al cerrar
    cap.release()