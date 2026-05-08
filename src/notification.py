import smtplib
import threading
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from pathlib import Path
from datetime import datetime
from config import EMAIL_CONFIG

def _send_email_worker(image_path: Path | str, details: str, timestamp: str):
    """
    Lógica interna para envío de correo (ejecutada en hilo secundario).
    """
    try:
        msg = MIMEMultipart('related')
        msg['Subject'] = f"ALERTA CRÍTICA: Acceso No Autorizado - {timestamp}"
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['To'] = EMAIL_CONFIG['security_email']

        # Definimos un ID único para la imagen que usaremos en el HTML
        content_id = "security_event_image"

        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2 style="color: #d9534f;"> Alerta de Seguridad: Acceso No Autorizado</h2>
                <p>Se ha detectado un intento de acceso no autorizado en el sistema.</p>
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; border: 1px solid #ddd;">
                    <p><b>Detalles del evento:</b></p>
                    <ul style="list-style: none; padding-left: 0;">
                        <li><b> Fecha y Hora:</b> {timestamp}</li>
                        <li><b> Motivo:</b> {details}</li>
                    </ul>
                </div>
                <p><b>Captura del rostro detectado:</b></p>
                <p><img src="cid:{content_id}" style="border: 3px solid #d9534f; border-radius: 8px; max-width: 500px; height: auto;"></p>
                <hr style="border: 0; border-top: 1px solid #eee;">
                <p style="font-size: 12px; color: #777;">Este es un correo automático generado por el Sistema PID II.</p>
            </body>
        </html>
        """
        msg.attach(MIMEText(html_body, 'html'))

        # Adjuntar la imagen
        image_path = Path(image_path)
        if image_path.exists():
            with open(image_path, 'rb') as f:
                img_data = f.read()
                image = MIMEImage(img_data)
                # Asignamos el Content-ID para que el HTML pueda encontrar la imagen
                image.add_header('Content-ID', f'<{content_id}>')
                msg.attach(image)
        else:
            print(f" [!] Advertencia: El archivo de imagen no se encontró para adjuntar: {image_path}")

        # Conexión al servidor SMTP
        with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
            # Mailtrap soporta TLS en 587 y 2525
            if EMAIL_CONFIG['smtp_port'] in [587, 2525]:
                server.starttls()
            
            server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
            server.send_message(msg)
            
        print(f" Correo de alerta enviado a {EMAIL_CONFIG['security_email']}")
    except Exception as e:
        print(f" Error al enviar correo de alerta: {e}")

def send_security_alert(image_path: Path | str, details: str = "Intruso detectado"):
    """
    Inicia el envío de la alerta en un hilo separado para no bloquear la GUI.
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Creamos un hilo para que la app no se detenga mientras envía el correo
    thread = threading.Thread(
        target=_send_email_worker, 
        args=(image_path, details, timestamp),
        daemon=True
    )
    thread.start()
    return True