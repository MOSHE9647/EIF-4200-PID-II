# EIF-4200-PID-II

## Requisitos previos

- [Anaconda](https://www.anaconda.com/download) instalado
- Visual Studio Code instalado
- Extensión **Python** de Microsoft instalada en VS Code

---

## 1. Crear el ambiente conda 

Abre una terminal y ejecuta:

```powershell
conda create -n Caralaboratorio(reemplazar por el nombre del ambiente) python=3.13.13```

---

## activar en anaconda 

conda activate Caralaboratorio(reemplazar por el nombre del ambiente)


## 2. Seleccionar el intérprete en VS Code

1. Presiona `Ctrl+Shift+P`
2. Escribe **Python: Select Interpreter**
3. Selecciona el ambiente `conda: Caralaboratorio`

Si no aparece en la lista, elige **Enter interpreter path...** y navega a:

```
C:\Users\<tu_usuario>\anaconda3\envs\Caralaboratorio\python.exe
```

## 2. Activar el ambiente en visual studio code

Si `conda` no se reconoce en PowerShell, usa el hook de Anaconda directamente:

```powershell
(C:\Users\<tu_usuario>\anaconda3\shell\condabin\conda-hook.ps1) ; conda activate Caralaboratorio(cambiar por el nombre del ambiente )
```

> Reemplaza `<tu_usuario>` con tu nombre de usuario de Windows.

El prompt debe cambiar a en visual:

```
(Caralaboratorio) PS C:\PROYECTO_LABORATORIO\EIF-4200-PID-II>
```

---

## 3. Instalar los paquetes

Con el ambiente activo:

```powershell
pip install mysql-connector-python cryptography
```

Para verificar que se instalaron correctamente:

```powershell
pip list | Select-String -Pattern "mysql|cryptography"
```

Debe mostrar algo como:

```
cryptography               47.0.0
mysql-connector-python     9.7.0
```

revisar que se instalaron correctamente cambiar los datos por su ruta:

C:/Users/keyna/anaconda3/envs/TareaBusquedaHeuristica/python.exe -c "import mysql.connector; import cryptography; print(' Dependencias OK')"


---

## 5. Ejecutar el script

```powershell esto hace datos de prueba
python src/database.py
```

---

## Notas importantes

- El archivo `secret.key` se genera automáticamente la primera vez que se ejecuta el script. **No lo elimines** ni lo compartas — es la clave de cifrado de los datos en la base de datos.
- Si borras `secret.key` y la base de datos ya tiene datos cifrados, los nombres de los empleados no podrán descifrarse. En ese caso deberás limpiar las tablas y volver a insertar los datos.


para usar para registrar un nuevo empleado
db = DatabaseManager()
db.connect()
db.registrar_nuevo_empleado("Nombre", "EMP004", "ruta/imagen.jpg")
