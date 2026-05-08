# config.py
# Configuración de la base de datos MySQL
import os
from cryptography.fernet import Fernet

DB_CONFIG = {
    'host': 'tebnhf.h.filess.io',
    'user': 'bdPIDII_wrongpiece',         
    'password': 'FacialPID2',          
    'database': 'bdPIDII_wrongpiece',
    'port': 3307,
    'raise_on_warnings': True,
    'use_pure': True,  # Para mejor compatibilidad
    'connect_timeout': 30
}

# Configuración para cifrado
SECRET_KEY_FILE = 'secret.key'

# ============================================
# Configuración de Alertas por Correo
# ============================================
# Ejemplo de configuración para Mailtrap en config.py
EMAIL_CONFIG = {
    'smtp_server': 'sandbox.smtp.mailtrap.io',
    'smtp_port': 2525,
    'sender_email': 'bf66228a5a479d', 
    'sender_password': 'b05e3b6bf664f8',
    'security_email': 'keyna.castro.fuentes@est.una.ac.cr'
}


# Rutas del sistema
PATHS = {
    'known_faces': 'data/known_faces/',
    'unknown_faces': 'data/unknown_faces/',
    'audit_logs': 'data/audit_logs/'
}