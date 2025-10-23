# TFGII Modelo Cinemático Inverso de un robot GoFa

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=jmg0136_TFG_MCI_GoFa&metric=alert_status&token=42c8585eac04e25aa34173dac261691defcb7c94)](https://sonarcloud.io/summary/new_code?id=jmg0136_TFG_MCI_GoFa) [![Bugs](https://sonarcloud.io/api/project_badges/measure?project=jmg0136_TFG_MCI_GoFa&metric=bugs&token=42c8585eac04e25aa34173dac261691defcb7c94)](https://sonarcloud.io/summary/new_code?id=jmg0136_TFG_MCI_GoFa) [![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=jmg0136_TFG_MCI_GoFa&metric=code_smells&token=42c8585eac04e25aa34173dac261691defcb7c94)](https://sonarcloud.io/summary/new_code?id=jmg0136_TFG_MCI_GoFa) [![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=jmg0136_TFG_MCI_GoFa&metric=duplicated_lines_density&token=42c8585eac04e25aa34173dac261691defcb7c94)](https://sonarcloud.io/summary/new_code?id=jmg0136_TFG_MCI_GoFa)

<p align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/3/3c/Flask_logo.svg" alt="Flask" width="48"/>
  <img src="https://upload.wikimedia.org/wikipedia/commons/2/2d/Tensorflow_logo.svg" alt="TensorFlow" width="48"/>
  <img src="https://upload.wikimedia.org/wikipedia/commons/b/b9/Nvidia_CUDA_Logo.jpg" alt="CUDA" width="48"/>
</p>

## Descripción

Este proyecto es una plataforma web robusta y multiplataforma para la gestión, entrenamiento y despliegue de modelos de Machine Learning aplicados a robótica (ABB GoFa). Permite la gestión de configuraciones, entrenamiento y predicción desde una interfaz web segura, con almacenamiento de configuraciones en SQLite y protección CSRF. Aprovecha las características de procesamiento paralelo de las tarjetas gráficas Nvidia gracias a su tecnología CUDA (es necesario disponer de una tarjeta gráfica Nvidia).

### Funcionalidades principales
- **Interfaz web Flask** para entrenamiento y predicción de modelos ML.
- **Procesamiento paralelo con Nvidia CUDA** para aprovechar el hardware específico.
- **Gestión de configuraciones**: guardar, cargar y eliminar configuraciones de entrenamiento en SQLite.
- **Predicción online**: selección de modelo y predicción desde la web.
- **Protección CSRF** en formularios y endpoints sensibles.
- **Selección de archivos/carpetas** multiplataforma.
- **Pruebas automáticas**: unitarias, integración y end-to-end con pytest.

### Tecnologías utilizadas

- <img src="https://upload.wikimedia.org/wikipedia/commons/3/3c/Flask_logo.svg" alt="Flask" width="24"/> **Flask** (backend web, blueprints, CSRF)
- <img src="https://upload.wikimedia.org/wikipedia/commons/2/2d/Tensorflow_logo.svg" alt="TensorFlow" width="24"/> **TensorFlow/Keras** (entrenamiento y predicción ML)
- <img src="https://upload.wikimedia.org/wikipedia/commons/e/ed/Pandas_logo.svg" alt="pandas" width="24"/> **pandas** (procesado de datos)
- <img src="https://upload.wikimedia.org/wikipedia/commons/3/38/SQLite370.svg" alt="SQLite" width="24"/> **SQLite** (almacenamiento de configuraciones)
- <img src="https://upload.wikimedia.org/wikipedia/commons/6/6a/JavaScript-logo.png" alt="JavaScript" width="24"/> **JavaScript** (frontend, AJAX, modales)
- <img src="https://upload.wikimedia.org/wikipedia/commons/b/ba/Pytest_logo.svg" alt="pytest" width="24"/> **pytest** (pruebas automáticas)
- <img src="https://upload.wikimedia.org/wikipedia/commons/3/3c/Flask_logo.svg" alt="Flask-WTF" width="24"/> **Flask-WTF/WTForms** (formularios seguros)
- <img src="https://upload.wikimedia.org/wikipedia/commons/b/b9/Nvidia_CUDA_Logo.jpg" alt="Nvidia CUDA" width="24"/> **Nvidia CUDA** (computación paralela)

### Instalación rápida

```bash
# Clona el repositorio y entra en la carpeta
cd TFG_MCI_GoFa

# Si no dispones de la herramienta de entornos virtuales de Python, instala con:
sudo apt install python3.12-venv

# Crea un entorno virtual y actívalo
python3 -m venv flask_app_venv
source flask_app_venv/bin/activate

# Instala las dependencias
pip install -r requirements.txt

# Ejecuta la aplicación (¡IMPORTANTE!)
# Para evitar errores de imports, ejecuta SIEMPRE desde la carpeta dónde se encuentre flask_app/:
python -m flask_app.app

# Si ejecutas con `python flask_app/app.py` pueden producirse errores de importación.
# Los tests y la app funcionarán correctamente con la instrucción anterior en cualquier plataforma.
```

### Ejecución de tests

```bash
pytest
```

### Estructura principal
- `flask_app/` — Código fuente de la aplicación Flask
- `DataSets/` — Datos de entrenamiento y prueba
- `Memoria/` — Documentación y memoria del TFG
- `Notebooks/` — Cuadernos de experimentación ML / Interfaz alternativa
- `Sockets/` — Scripts de comunicación cliente-servidor

---

**Autor:** Jairo Montes González — TFG MCI GoFa — 2025 (c)