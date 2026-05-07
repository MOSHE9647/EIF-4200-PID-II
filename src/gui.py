import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2

class AccessControlGUI:
    def __init__(self, root):
        """
        Inicializa la ventana principal y los componentes visuales.
        """
        self.root = root
        self.root.title("Sistema Avanzado de Identificación Facial")
        self.root.geometry("1100x650")
        self.root.configure(padx=10, pady=10)

        # Contenedor principal
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Panel Izquierdo: Video en Vivo ---
        self.video_frame = ttk.LabelFrame(self.main_frame, text="Monitoreo en Tiempo Real")
        self.video_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Etiqueta donde se renderizarán los frames de OpenCV con los bounding boxes
        self.video_label = ttk.Label(self.video_frame)
        self.video_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- Panel Derecho: Registros ---
        self.log_frame = ttk.LabelFrame(self.main_frame, text="Últimos Registros")
        self.log_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Tabla (Treeview) para mostrar registros de la base de datos
        columns = ("ID", "Empleado", "Hora", "Estado")
        self.tree = ttk.Treeview(self.log_frame, columns=columns, show="headings", height=25)
        
        # Configuración de cabeceras y anchos de columna
        self.tree.heading("ID", text="ID")
        self.tree.column("ID", width=40, anchor=tk.CENTER)
        
        self.tree.heading("Empleado", text="Empleado")
        self.tree.column("Empleado", width=150)
        
        self.tree.heading("Hora", text="Fecha/Hora")
        self.tree.column("Hora", width=130, anchor=tk.CENTER)
        
        self.tree.heading("Estado", text="Estado")
        self.tree.column("Estado", width=100, anchor=tk.CENTER)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def update_video_frame(self, cv2_image):
        """
        Recibe un frame procesado (con bounding boxes) y lo actualiza en la GUI.
        Totalmente agnóstico al motor de reconocimiento.
        """
        if cv2_image is None:
            return

        # Convertir de BGR (OpenCV) a RGB (Pillow/Tkinter)
        rgb_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)
        tk_image = ImageTk.PhotoImage(image=pil_image)

        # Actualizar la etiqueta
        self.video_label.config(image=tk_image)
        self.video_label.image = tk_image # Prevenir recolección de basura

    def update_logs(self, logs_list):
        """
        Actualiza el panel lateral en tiempo real con los registros de la DB.
        logs_list debe ser una lista de tuplas: [(id, nombre, hora, estado), ...]
        """
        # Limpiar registros actuales
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        # Insertar los nuevos registros [cite: 57]
        for log in logs_list:
            # Se asume que el nombre ya viene descifrado desde la lógica de DB [cite: 110]
            self.tree.insert("", tk.END, values=log)