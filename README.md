# EIF-4200-PID-II: Sistema Avanzado de Identificación Facial

## Requisitos previos

- [Anaconda](https://www.anaconda.com/download) instalado en el sistema.
- Visual Studio Code instalado.
- Extensión **Python** de Microsoft instalada en VS Code.

---

## 1. Crear el ambiente Conda 

Abre una terminal (Anaconda Prompt o PowerShell) y ejecuta:

```powershell
conda create -n sistema_facial python=3.13.13
```
*(Puedes reemplazar `sistema_facial` por el nombre que prefieras para tu entorno).*

---

## 2. Activar el ambiente

**Opción A: Desde Anaconda Prompt / CMD**
```powershell
conda activate sistema_facial
```

**Opción B: Desde PowerShell (en VS Code)**
Si `conda` no se reconoce directamente en PowerShell, usa el hook de Anaconda:
```powershell
(C:\Users\<tu_usuario>\anaconda3\shell\condabin\conda-hook.ps1) ; conda activate sistema_facial
```
> *Nota: Reemplaza `<tu_usuario>` con tu nombre de usuario de Windows.* El prompt de tu terminal debe cambiar para mostrar el ambiente activo:
```powershell
(sistema_facial) PS C:\ruta\a\tu\proyecto\EIF-4200-PID-II>
```

---

## 3. Seleccionar el intérprete en VS Code

1. Presiona `Ctrl+Shift+P` dentro de VS Code.
2. Escribe y selecciona **Python: Select Interpreter**.
3. Elige el ambiente `conda: sistema_facial` en la lista.

Si no aparece automáticamente, elige **Enter interpreter path...** y navega hasta:
```text
C:\Users\<tu_usuario>\anaconda3\envs\sistema_facial\python.exe
```

---

## 4. Instalación de Dependencias

Con el ambiente activo en tu terminal, instalaremos todas las librerías necesarias del proyecto (Visión, Base de Datos, Interfaz y Cifrado) utilizando el archivo de requerimientos.

Asegúrate de estar en la carpeta raíz del proyecto y ejecuta:

```powershell
pip install -r requirements.txt
```
*(Este comando instalará automáticamente la versión precompilada de `dlib`, `opencv-python`, `face_recognition`, `mysql-connector-python`, `cryptography` y `Pillow`).*

### Verificación de la instalación
Para comprobar que los módulos críticos se instalaron correctamente, ejecuta este comando ajustando la ruta a tu usuario:

```powershell
C:/Users/<tu_usuario>/anaconda3/envs/sistema_facial/python.exe -c "import cv2; import face_recognition; import mysql.connector; import cryptography; print(' ¡Todas las dependencias están OK!')"
```

---

## 5. Ejecución y Pruebas

Para inicializar la base de datos y generar los datos de prueba, ejecuta el script principal de la base de datos:

```powershell
python src/database.py
```

### Ejemplo de uso (Registro de Empleados)
Si deseas registrar un nuevo empleado desde otro módulo, la sintaxis a utilizar es la siguiente:

```python
from database import DatabaseManager

db = DatabaseManager()
db.connect()
db.registrar_nuevo_empleado("Nombre Empleado", "EMP004", "ruta/imagen.jpg")
```

---

## ⚠️ Notas Importantes de Seguridad

- **Manejo de Claves:** El archivo `secret.key` se genera automáticamente en la raíz del proyecto la primera vez que se ejecuta el script de la base de datos. **NO lo elimines, modifiques ni lo subas a GitHub** (asegúrate de que esté en tu `.gitignore`). Esta es la llave simétrica para el cifrado AES.
- **Pérdida de Claves:** Si borras o pierdes `secret.key` y la base de datos ya contiene registros cifrados, será matemáticamente imposible descifrar los nombres de los empleados. En ese escenario, la única solución será truncar (vaciar) las tablas en MySQL y volver a registrar a todo el personal.