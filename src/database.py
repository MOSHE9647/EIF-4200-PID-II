import mysql.connector
from mysql.connector import Error
from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
import base64
import hashlib
from datetime import datetime
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from config import DB_CONFIG, SECRET_KEY_FILE

class DatabaseManager:
    def __init__(self, host=None, user=None, password=None, database=None, port=None):
        """
        Inicializa la conexión con la base de datos
        """
        self.host = host or DB_CONFIG['host']
        self.user = user or DB_CONFIG['user']
        self.password = password or DB_CONFIG['password']
        self.database = database or DB_CONFIG['database']
        self.port = port or DB_CONFIG['port']
        self.connection = None
        self.cursor = None
        self.cipher = self._load_or_create_key()
        
    def _load_or_create_key(self):
        """
        Carga o crea la clave de cifrado para proteger los datos
        """
        key_file = SECRET_KEY_FILE
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
        
        return Fernet(key)
    
    def encrypt_data(self, data):
        """
        Cifra datos sensibles
        """
        if data is None:
            return None
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_data(self, encrypted_data):
        """
        Descifra datos sensibles
        """
        if encrypted_data is None:
            return None
        try:
            return self.cipher.decrypt(encrypted_data.encode()).decode()
        except InvalidToken:
            return None
    
    def connect(self):
        """
        Establece conexión con MySQL
        """
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                use_pure=DB_CONFIG.get('use_pure', True),
                raise_on_warnings=DB_CONFIG.get('raise_on_warnings', True),
                connect_timeout=DB_CONFIG.get('connect_timeout', 30)
            )
            self.cursor = self.connection.cursor(dictionary=True)
            print(" Conexión exitosa a la base de datos")
            return True
        except Error as e:
            print(f" Error al conectar a MySQL: {e}")
            return False
    
    def disconnect(self):
        """
        Cierra la conexión con la base de datos
        """
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print(" Conexión a base de datos cerrada")
    
    def crear_tablas(self):
        """
        Crea las tablas necesarias si no existen
        """
        queries = [
            """
            CREATE TABLE IF NOT EXISTS tb_empleado (
                empleado_id INT PRIMARY KEY AUTO_INCREMENT,
                nombre VARCHAR(255) NOT NULL,
                codigo_empleado VARCHAR(50) UNIQUE NOT NULL,
                ruta_imagen VARCHAR(500) NOT NULL,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                activo BOOLEAN DEFAULT TRUE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS tb_registro_accesos (
                registro_accesos_id INT PRIMARY KEY AUTO_INCREMENT,
                empleado_id INT,
                fecha_hora DATETIME NOT NULL,
                estado_acceso ENUM('AUTORIZADO', 'NO_AUTORIZADO', 'INTENTO_FALLIDO') NOT NULL,
                motivo VARCHAR(255),
                FOREIGN KEY (empleado_id) REFERENCES tb_empleado(empleado_id) ON DELETE SET NULL
            )
            """
        ]
        
        for query in queries:
            try:
                self.cursor.execute(query)
                self.connection.commit()
            except Error as e:
                if getattr(e, "errno", None) == 1050:
                    continue
                print(f"Error al crear tabla: {e}")
    
    def agregar_empleado(self, nombre, codigo_empleado, ruta_imagen):
        """
        Agrega un nuevo empleado con datos cifrados
        """
        nombre_cifrado = self.encrypt_data(nombre)
        
        query = """
        INSERT INTO tb_empleado (nombre, codigo_empleado, ruta_imagen)
        VALUES (%s, %s, %s)
        """
        
        try:
            self.cursor.execute(query, (nombre_cifrado, codigo_empleado, ruta_imagen))
            self.connection.commit()
            empleado_id = self.cursor.lastrowid
            print(f" Empleado '{nombre}' agregado exitosamente con ID: {empleado_id}")
            return empleado_id
        except Error as e:
            print(f" Error al agregar empleado: {e}")
            return None
    
    def obtener_empleado_por_codigo(self, codigo_empleado):
        """
        Obtiene un empleado por su código (descifrando el nombre)
        """
        query = "SELECT * FROM tb_empleado WHERE codigo_empleado = %s AND activo = TRUE"
        
        try:
            self.cursor.execute(query, (codigo_empleado,))
            result = self.cursor.fetchone()
            
            if result:
                # Descifrar el nombre antes de retornar
                result['nombre_descifrado'] = self.decrypt_data(result['nombre'])
            
            return result
        except Error as e:
            print(f" Error al obtener empleado: {e}")
            return None
    
    def obtener_empleado_por_id(self, empleado_id):
        """
        Obtiene un empleado por su ID (descifrando el nombre)
        """
        query = "SELECT * FROM tb_empleado WHERE empleado_id = %s AND activo = TRUE"
        
        try:
            self.cursor.execute(query, (empleado_id,))
            result = self.cursor.fetchone()
            
            if result:
                result['nombre_descifrado'] = self.decrypt_data(result['nombre'])
            
            return result
        except Error as e:
            print(f" Error al obtener empleado: {e}")
            return None
    
    def obtener_todos_empleados(self):
        """
        Obtiene todos los empleados activos (descifrando nombres)
        """
        query = "SELECT * FROM tb_empleado WHERE activo = TRUE"
        
        try:
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            
            for result in results:
                result['nombre_descifrado'] = self.decrypt_data(result['nombre'])
            
            return results
        except Error as e:
            print(f" Error al obtener empleados: {e}")
            return []
    
    def registrar_acceso(self, empleado_id, estado_acceso, motivo=None):
        """
        Registra un intento de acceso en el sistema
        estados: 'AUTORIZADO', 'NO_AUTORIZADO', 'INTENTO_FALLIDO'
        """
        query = """
        INSERT INTO tb_registro_accesos (empleado_id, fecha_hora, estado_acceso, motivo)
        VALUES (%s, %s, %s, %s)
        """
        
        try:
            self.cursor.execute(query, (empleado_id, datetime.now(), estado_acceso, motivo))
            self.connection.commit()
            print(f" Acceso registrado: {estado_acceso}")
            return True
        except Error as e:
            print(f" Error al registrar acceso: {e}")
            return False
    
    def obtener_ultimos_registros(self, limite=10):
        """
        Obtiene los últimos registros de acceso con información del empleado
        """
        query = """
        SELECT 
            r.registro_accesos_id,
            r.fecha_hora,
            r.estado_acceso,
            r.motivo,
            e.empleado_id as empleado_id,
            e.nombre,
            e.codigo_empleado
        FROM tb_registro_accesos r
        LEFT JOIN tb_empleado e ON r.empleado_id = e.empleado_id
        ORDER BY r.fecha_hora DESC
        LIMIT %s
        """
        
        try:
            self.cursor.execute(query, (limite,))
            results = self.cursor.fetchall()
            
            for result in results:
                if result['nombre']:
                    result['nombre_descifrado'] = self.decrypt_data(result['nombre'])
            
            return results
        except Error as e:
            print(f" Error al obtener registros: {e}")
            return []
    
    def validar_permiso_acceso(self, codigo_empleado):
        """
        Valida si un empleado tiene permiso de acceso
        Retorna: (bool, dict_empleado, mensaje)
        """
        empleado = self.obtener_empleado_por_codigo(codigo_empleado)
        
        if empleado:
            # Registrar acceso autorizado
            self.registrar_acceso(empleado['empleado_id'], 'AUTORIZADO')
            return True, empleado, " Acceso autorizado"
        else:
            # Registrar acceso no autorizado
            self.registrar_acceso(None, 'NO_AUTORIZADO', f"Código {codigo_empleado} no registrado")
            return False, None, " Acceso denegado: Personal no autorizado"
    
    def registrar_nuevo_empleado(self, nombre, codigo_empleado, ruta_imagen):
        """
        Agrega un empleado y registra su acceso inicial en una sola operación.
        Retorna el empleado_id si fue exitoso, None si falló.
        """
        empleado_id = self.agregar_empleado(nombre, codigo_empleado, ruta_imagen)
        if empleado_id:
            self.registrar_acceso(empleado_id, 'AUTORIZADO', 'Registro inicial del empleado')
        return empleado_id

    def obtener_estadisticas(self):
        """
        Obtiene estadísticas del sistema
        """
        stats = {}
        
        # Total de empleados
        self.cursor.execute("SELECT COUNT(*) as total FROM tb_empleado WHERE activo = TRUE")
        stats['total_empleados'] = self.cursor.fetchone()['total']
        
        # Total de accesos hoy
        self.cursor.execute("""
            SELECT COUNT(*) as total FROM tb_registro_accesos 
            WHERE DATE(fecha_hora) = CURDATE()
        """)
        stats['accesos_hoy'] = self.cursor.fetchone()['total']
        
        # Total de accesos no autorizados hoy
        self.cursor.execute("""
            SELECT COUNT(*) as total FROM tb_registro_accesos 
            WHERE DATE(fecha_hora) = CURDATE() 
            AND estado_acceso = 'NO_AUTORIZADO'
        """)
        stats['accesos_denegados_hoy'] = self.cursor.fetchone()['total']
        
        return stats

# Función de prueba
def probar_base_datos(codigo_prueba="EMP001"):
    """
    Función para probar la conexión y operaciones de la base de datos
    """
    db = DatabaseManager()
    
    if db.connect():
        # Crear tablas
        db.crear_tablas()

        # Solo insertar empleados de ejemplo si la tabla está vacía
        db.cursor.execute("SELECT COUNT(*) as total FROM tb_empleado")
        if db.cursor.fetchone()['total'] == 0:
            empleados_ejemplo = [
                ("Juan Pérez", "EMP001", "data/known_faces/juan_perez.jpg"),
                ("María García", "EMP002", "data/known_faces/maria_garcia.jpg"),
                ("Carlos López", "EMP003", "data/known_faces/carlos_lopez.jpg")
            ]
            for nombre, codigo, ruta in empleados_ejemplo:
                db.registrar_nuevo_empleado(nombre, codigo, ruta)
        
        # Probar validación de acceso
        print("\n--- Probando validación de acceso ---")
        autorizado, empleado, mensaje = db.validar_permiso_acceso(codigo_prueba)
        print(mensaje)
        if empleado:
            print(f"Empleado: {empleado['nombre_descifrado']}")
        
        # Probar acceso no autorizado
        autorizado, empleado, mensaje = db.validar_permiso_acceso("EMP999")
        print(mensaje)
        
        # Mostrar últimos registros
        print("\n--- Últimos registros de acceso ---")
        registros = db.obtener_ultimos_registros(5)
        for registro in registros:
            print(f"{registro['fecha_hora']} - {registro['estado_acceso']} - Empleado: {registro.get('nombre_descifrado', 'N/A')}")
        
        # Mostrar estadísticas
        print("\n--- Estadísticas del sistema ---")
        stats = db.obtener_estadisticas()
        for key, value in stats.items():
            print(f"{key}: {value}")
        
        db.disconnect()

if __name__ == "__main__":
    codigo = sys.argv[1] if len(sys.argv) > 1 else "EMP001"
    probar_base_datos(codigo)
