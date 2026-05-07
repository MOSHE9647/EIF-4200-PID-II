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
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': 'tu_correo@gmail.com',
    'sender_password': 'tu_contraseña_o_app_password',
    'security_email': 'seguridad@empresa.com'
}

# Rutas del sistema
PATHS = {
    'known_faces': 'data/known_faces/',
    'unknown_faces': 'data/unknown_faces/',
    'audit_logs': 'data/audit_logs/'
}