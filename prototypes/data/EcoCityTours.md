# Eco City Tours

## TFG Ingeniería Informática - Fernando Pisot

[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=fps1001_TFGII_FPisot&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=fps1001_TFGII_FPisot)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=fps1001_TFGII_FPisot&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=fps1001_TFGII_FPisot)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=fps1001_TFGII_FPisot&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=fps1001_TFGII_FPisot)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=fps1001_TFGII_FPisot&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=fps1001_TFGII_FPisot) 
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=fps1001_TFGII_FPisot&metric=bugs)](https://sonarcloud.io/summary/new_code?id=fps1001_TFGII_FPisot) 


[![GitHub issues](https://img.shields.io/github/issues-closed/fps1001/TFGII_FPisot)](https://github.com/fps1001/TFGII_FPisot/issues)
[![Wiki](https://img.shields.io/badge/wiki-available-brightgreen)](https://github.com/fps1001/TFGII_FPisot/wiki)
![GitHub Release](https://img.shields.io/github/v/release/fps1001/TFGII_FPisot?label=Release)
[![Workflow Status](https://github.com/fps1001/TFGII_FPisot/actions/workflows/main.yml/badge.svg)](https://github.com/fps1001/TFGII_FPisot/actions)
[![Zube](https://img.shields.io/badge/zube-managed-blue?logo=zube)](https://zube.io/)
---

Este repositorio contiene el código fuente de **Eco City Tours**, una aplicación móvil que propone rutas turísticas generadas con tecnologías GIS, enriquecidas mediante modelos de lenguaje (LLM). La aplicación promueve rutas no motorizadas optimizadas para ciclistas y peatones, contribuyendo a los Objetivos de Desarrollo Sostenible (ODS11).

---
## 🎓 Información Académica
Este proyecto forma parte del Trabajo de Fin de Grado (TFG) de Ingeniería Informática bajo la supervisión de:

- **Carlos López Nozal** <p>
    Departamento de Ingeniería Informática, Universidad de Burgos
    - Contacto: clopezno@ubu.es

---
## 📌 Objetivos del Proyecto

- **Promoción de Rutas No Motorizadas**: Fomentar el uso de rutas sostenibles.
- **Enriquecimiento de Datos**: Uso de LLM y Google Places para información turística detallada.
- **ODS11**: Apoyo a la creación de ciudades y comunidades sostenibles.

---

## 🛠️ Tecnologías Utilizadas

- **Flutter & Dart**: Desarrollo de la interfaz y lógica de la aplicación.
- **Modelos de Lenguaje (LLM)**: Enriquecimiento de datos y generación de información turística.
- **Servicios Google**: API de Maps, Places y Directions para optimización y visualización de rutas.
- **Firebase**: Gestión de base de datos y análisis de errores.

---

## 🚀 Funcionalidades Principales

1. Generación de rutas personalizadas para ciclistas y peatones.
2. Información enriquecida sobre puntos de interés turístico.
3. Optimización de rutas con datos GIS.
4. Integración con Firebase para almacenamiento y monitoreo de errores.

---

## ⚙️ Compilación, Instalación y Ejecución del Proyecto

### **Obtención del Código Fuente**

1. Asegúrate de tener [Git](https://git-scm.com/) instalado.
2. Clona el repositorio ejecutando:
    ```sh
    git clone https://github.com/fps1001/TFGII_FPisot.git
    ```
3. Cambia al directorio del proyecto:
    ```sh
    cd TFGII_FPisot/project-app/project_app
    ```

---

### **Configuración de Servicios Externos**

#### **Google Cloud Platform**
1. Regístrate en [Google Cloud Platform](https://cloud.google.com/) y crea un proyecto.
2. Activa las siguientes APIs desde la consola:
    - **Maps SDK for Android**
    - **Places API**
    - **Directions API**
    - **Generative AI API (Gemini)**
3. Genera claves API para cada servicio y colócalas en un archivo `.env` en la raíz del proyecto con el formato:
    ```env
    GOOGLE_API_KEY=<TU_CLAVE>
    GEMINI_API_KEY=<TU_CLAVE>
    GOOGLE_DIRECTIONS_API_KEY=<TU_CLAVE>
    GOOGLE_PLACES_API_KEY=<TU_CLAVE>
    ```

#### **Firebase**
1. Regístrate en [Firebase Console](https://firebase.google.com/) y crea un proyecto llamado `eco-city-tour`.
2. Configura los servicios:
    - **Cloud Firestore**: Habilita Firestore en modo "Producción".
    - **Crashlytics**: Integra Crashlytics siguiendo las instrucciones en Firebase Console.
3. Descarga el archivo `google-services.json` y colócalo en `/android/app/`.
4. Agrega las siguientes variables al archivo `.env`:
    ```env
    FIREBASE_API_KEY=<TU_CLAVE>
    FIREBASE_APP_ID=<TU_CLAVE>
    FIREBASE_MESSAGING_SENDER_ID=<TU_CLAVE>
    FIREBASE_PROJECT_ID=eco-city-tour
    FIREBASE_STORAGE_BUCKET=eco-city-tour.appspot.com
    FIREBASE_PACKAGE_NAME=com.example.project_app
    FIREBASE_PROJECT_NUMBER=<TU_NUMERO>
    MOBILESDK_APP_ID=<TU_CLAVE>
    ```

---

### **Compilación y Ejecución**

1. Asegúrate de que el archivo `.env` está configurado correctamente.
2. Instala las dependencias:
    ```sh
    flutter pub get
    ```
3. Ejecuta la aplicación en un emulador o dispositivo:
    ```sh
    flutter run
    ```

---

## 🔍 Pruebas del Sistema

El sistema fue sometido a diversas pruebas para garantizar su calidad y funcionalidad:

- **Pruebas Unitarias**: Validación de componentes individuales.
- **Pruebas de Integración**: Verificación de interacción entre módulos.
- **Pruebas de Usuario**: Feedback recopilado de usuarios finales.

---

## 🤝 Contribución

¡Contribuciones son bienvenidas! Sigue estos pasos para colaborar:

1. Realiza un fork del repositorio.
2. Crea una nueva rama (`git checkout -b feature/nueva-funcionalidad`).
3. Realiza los cambios y haz commit (`git commit -am 'Descripción del cambio'`).
4. Empuja tus cambios (`git push origin feature/nueva-funcionalidad`).
5. Abre un Pull Request.

---

## 📄 Licencia

Este proyecto está licenciado bajo los términos de la GNU General Public License v3.0. Consulta el archivo [LICENSE](LICENSE) para más detalles o a través del siguiente enlace:  
[https://www.gnu.org/licenses/gpl-3.0.txt](https://www.gnu.org/licenses/gpl-3.0.txt).

---

## 📬 Contacto

Si tienes preguntas o necesitas más información, no dudes en contactarme:

- **Correo Electrónico**: fpisot@gmail.com / fps1001@alu.ubu.es  
- **LinkedIn**: [Fernando Pisot](https://www.linkedin.com/in/fernando-pisot-17b93b251/)

---

¡Gracias por tu interés en este proyecto! 💡