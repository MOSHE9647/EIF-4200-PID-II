# EIF-4200 PID II - Sistema Avanzado de Identificacion Facial

Proyecto practico para control de acceso con reconocimiento facial, MySQL, interfaz grafica y cifrado de datos sensibles.

## Estado Actual

Ya existe:

- `src/database.py`: conexion a MySQL, creacion de tablas, registro de empleados, registro de accesos y cifrado/descifrado de nombres con `cryptography.Fernet`.
- `src/detector.py`: motor de reconocimiento facial. Carga rostros desde `data/known_faces`, compara contra video o imagen, dibuja cuadros verdes/rojos y registra eventos en la base de datos cuando recibe un `DatabaseManager`.
- `src/utils.py`: funciones auxiliares para rutas, lectura de imagenes, extraccion del codigo de empleado y captura de rostros desconocidos.
- `src/gui.py`: interfaz grafica y visualizacion del flujo de video.
- `config.py`: credenciales de base de datos, correo y rutas principales.

Pendiente de integracion final:

- Alertas sonoras y correo critico.
- Conexion completa entre GUI, motor facial, base de datos y notificaciones.

## 1. Crear Ambiente Conda

Abre Anaconda Prompt o PowerShell y ejecuta:

```powershell
conda create -n PIDII_FACE python=3.10
conda activate PIDII_FACE
```

Se recomienda Python 3.10 para evitar problemas de compatibilidad entre `dlib`, `face_recognition` y Windows.

## 2. Seleccionar Interprete en VS Code

1. Presiona `Ctrl+Shift+P`.
2. Busca `Python: Select Interpreter`.
3. Selecciona el ambiente `PIDII_FACE`.

Si no aparece, usa:

```text
C:\Anaconda\envs\PIDII_FACE\python.exe
```

## 3. Instalar Dependencias

Desde la carpeta raiz del proyecto:

```powershell
pip install -r requirements.txt
```

Si `face_recognition` o `dlib` falla en Windows, instala primero desde conda-forge:

```powershell
conda install -c conda-forge dlib face_recognition
pip install -r requirements.txt
```

Verificacion:

```powershell
python -c "import cv2; import face_recognition; import mysql.connector; import cryptography; print('Dependencias OK')"
```

## 4. Preparar Carpetas

Estructura esperada:

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

## 5. Base de Datos

El archivo `config.py` contiene la configuracion de MySQL:

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

Para probar un empleado especifico:

```powershell
python src/database.py EMP002
```

## 6. Probar Motor de Reconocimiento

Ver codigos cargados desde `data/known_faces`:

```powershell
python -c "from src.detector import FaceRecognitionEngine; engine=FaceRecognitionEngine(); print(engine.known_codes)"
```

Probar contra una imagen:

```python
from src.detector import FaceRecognitionEngine

engine = FaceRecognitionEngine()
matches = engine.recognize_image("ruta/a/imagen.jpg")
for match in matches:
    print(match)
```

Integracion con base de datos:

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
- No borres ni compartas `secret.key`.
- Si se pierde `secret.key`, los nombres ya guardados no se podran descifrar.
- Las capturas de desconocidos se guardan en `data/unknown_faces/` con nombre generado por fecha y hora.
