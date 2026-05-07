# EIF-4200 PID II - Sistema Facial

Proyecto practico para control de acceso con reconocimiento facial, MySQL y cifrado de datos sensibles.

## Estado actual


- `src/database.py`: conexion a MySQL, creacion de tablas, registro de empleados, registro de accesos y cifrado/descifrado de nombres con `cryptography.Fernet`.
- `src/detector.py`: motor de reconocimiento facial. Carga rostros desde `data/known_faces`, compara contra el video o una imagen, dibuja cuadros verdes/rojos y registra eventos en la base de datos cuando recibe un `DatabaseManager`.
- `src/utils.py`: funciones auxiliares para rutas, lectura de imagenes, extraccion del codigo de empleado y captura de rostros desconocidos.
- `config.py`: credenciales de base de datos, correo y rutas principales.


## Instalacion

### 1. Crear ambiente

```powershell
conda create -n facial_pid python=3.13
conda activate facial_pid
```

Si VS Code no activa conda en PowerShell, selecciona el interprete con:

1. `Ctrl+Shift+P`
2. `Python: Select Interpreter`
3. Selecciona el ambiente `facial_pid`

### 2. Instalar dependencias

```powershell
pip install -r requirements.txt
```

Nota: `face_recognition` puede requerir herramientas de compilacion en Windows porque depende de `dlib`. Si falla, una opcion practica es instalarlo desde conda-forge:

```powershell
conda install -c conda-forge dlib face_recognition
pip install mysql-connector-python cryptography opencv-python
```

### 3. Preparar carpetas

El proyecto espera esta estructura:

```text
data/
  known_faces/    # Fotos de empleados autorizados
  unknown_faces/  # Capturas de personas no reconocidas
src/
  database.py
  detector.py
  gui.py
  notification.py
  utils.py
main.py
config.py
secret.key
```

Las fotos autorizadas deben guardarse en `data/known_faces/` usando el codigo de empleado al inicio del nombre:

```text
EMP001.jpg
EMP002_maria.jpg
EMP003-carlos.jpg
```

El detector toma `EMP001`, `EMP002` o `EMP003` como codigo y lo consulta en MySQL.

## Base de datos

El archivo `config.py` contiene la configuracion de MySQL. Antes de probar, revisa:

```python
DB_CONFIG = {
    "host": "...",
    "user": "...",
    "password": "...",
    "database": "...",
    "port": 3307,
}
```

Para crear tablas y cargar datos de prueba:

```powershell
python src/database.py
```

`secret.key` es la clave local usada para cifrar y descifrar nombres. No se debe borrar ni compartir. Si se borra despues de insertar empleados, los nombres cifrados existentes ya no se podran descifrar.

## Probar solo el motor de reconocimiento

Ejemplo rapido desde una terminal Python:

```python
from src.detector import FaceRecognitionEngine

engine = FaceRecognitionEngine(auto_load=True)
print(engine.known_codes)
```

Para probar contra una imagen:

```python
from src.detector import FaceRecognitionEngine

engine = FaceRecognitionEngine()
matches = engine.recognize_image("ruta/a/imagen.jpg")
for match in matches:
    print(match)
```

Para integrarlo con base de datos:

```python
from src.database import DatabaseManager
from src.detector import FaceRecognitionEngine

db = DatabaseManager()
db.connect()
engine = FaceRecognitionEngine(db_manager=db)
```

Cuando la GUI entregue frames de OpenCV, debe llamar:

```python
frame_anotado, resultados = engine.process_frame(frame_bgr)
```

## Privacidad

- Los nombres se cifran antes de guardarse en `tb_empleado.nombre`.
- La aplicacion descifra el nombre solo cuando necesita mostrarlo.
- La clave `secret.key` queda fuera de la base de datos.
- Las capturas de desconocidos se guardan en `data/unknown_faces/` con nombres generados por fecha y hora.

## Siguiente paso de integracion

Cuando tus companeros tengan GUI y alertas, deben conectar:

- GUI -> `FaceRecognitionEngine.process_frame(frame_bgr)`
- Alertas -> usar `FaceMatch.autorizado == False` y `FaceMatch.evidence_path`
- Panel lateral -> `DatabaseManager.obtener_ultimos_registros()`
