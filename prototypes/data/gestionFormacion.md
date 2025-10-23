# Gestión de Formación

![PHPUnit](https://github.com/VictorVaqueroUBU/TFG/actions/workflows/symfony-tests.yml/badge.svg?event=pull_request)
![PHP](https://img.shields.io/badge/PHP-8.2-blue)
![Symfony](https://img.shields.io/badge/Symfony-7.1-lightgrey)
![Licencia](https://img.shields.io/badge/licencia-MIT-green)

## Introducción

Este proyecto es una aplicación web desarrollada en **Symfony** para la gestión de cursos formativos, sus ediciones, participantes y formadores, en el ámbito universitario.
- Gestión de cursos: creación, edición, eliminación y visualización de cursos por año de impartición.
- Gestión de ediciones: gestión de las ediciones de estos cursos con datos específicos como fechas de impartición, plazas y modalidad de impartición.
- Gestión de participantes: gestión de participantes y sus inscripciones a las ediciones existentes con datos específicos como fechas de solicitud, aptitud, nota, y certificados
- Gestión de formadores: gestión de formadores y su asignación a ediciones con datos específicos como gestión de retribuciones y evaluaciones por parte de los alumnos.

<p align="left">
   <img src="assets/images/login.png" alt="Portal del Gestor" width="800">
</p>

<p align="left">
   <img src="assets/images/portales.png" alt="Portal del Gestor" width="800">
</p>

<p align="left">
   <img src="assets/images/cursos.png" alt="Portal del Gestor" width="800">
</p>

---
## Cambios introducidos en los últimos Sprints

### Funcionalidades añadidas:
- **Portal del Formador**:
  - Visualización de ediciones abiertas y cerradas asignadas al formador.
  - Gestión de sesiones: creación de sesiones con fecha, hora de inicio, duración y tipo (presencial o virtual).
  - Registro de asistencia y calificación de participantes.
  - Validación del estado de las ediciones, sesiones y calificaciones, si las hubiera.
- **Portal del Gestor**:
  - Nueva herramienta de certificaciones de ediciones.
  - Visualización de la ficha formativa de un participante.
  - Visualización de las ediciones asignadas a un formador con sus estados actuales (abiertas, cerradas).
- **Documentación**:
  - Se ha añadido la memoria y la documentación técnica en formato docx y pdf a la documentación del proyecto.
- **Pruebas Unitarias y Calidad del Código**:
  - Implementación de pruebas para nuevas entidades y controladores.
  - Código validado con **PHPStan** para asegurar estándares de calidad.

### Pruebas realizadas:
- **PHPUnit**:
  - 107 pruebas unitarias pasadas exitosamente, con 489 aserciones.
- **PHPStan**:
  - Código analizado y corregido sin errores.
---

### Requisitos para el envío de correos
La aplicación utiliza un sistema de envío de correos para funciones como el registro de usuarios y otras notificaciones. Para habilitar esta funcionalidad, se requiere la instalación y configuración de un servidor local de correos, como Postfix.

## Tecnologías utilizadas

- **Symfony** 7.1
- **PHP** 8.2
- **MySQL** 8.0
- **PHPUnit** 9.6
- **PHPStan** 1.12
- **Composer**
- **Git**
- **Sequel Ace** (para la gestión visual de la base de datos)

---

## Instalación

1. Clona este repositorio en tu máquina local:

```bash
    git clone https://github.com/VictorVaqueroUBU/TFG.git
```

2. Ve al directorio del proyecto:

```bash
    cd tu-repositorio
```

3. Instala componentes de Symfony:

  - Entorno de pruebas
```bash
    composer install
```
  - Entorno de producción
```bash
    composer dump-env prod
    composer install --no-dev --optimize-autoloader
    APP_ENV=prod APP_DEBUG=0 bin/console cache:clear
```

4. Instalar componentes JavaScript

- Entorno de pruebas
```bash
    bin/console importmap:install
```
- Entorno de producción
```bash
    bin/console importmap:install
    bin/console asset-map:compile
```

5. Instalar componentes JavaScript

```bash
    bin/console sass:build
```

6. Crear base de datos

```mysql
    CREATE DATABASE IF NOT EXISTS formacion;
```

7. Crear usuario

```mysql
    CREATE USER IF NOT EXISTS 'Usuario'@'localhost' IDENTIFIED BY 'Clave';
```

8. Dar acceso

```mysql
    GRANT ALL PRIVILEGES ON formacion.* TO 'Usuario'@'localhost';
```

9. Configura las variables de entorno en el archivo `.env`. Asegúrate de incluir la URL de tu base de datos:

```dotenv
    DATABASE_URL="mysql://usuario:contraseña@127.0.0.1:3306/formacion?serverVersion=8.0"
    MAILER_DSN=native://default
    MAILER_SENDER="usuario@correo.es"
```

10. Realiza las migraciones de la base de datos:

```bash
    php bin/console doctrine:migrations:migrate
```

11. Levanta el servidor de desarrollo:

```bash
    symfony server:start
```

12. Accede a la aplicación en tu navegador en la dirección:

```bash
    https://localhost:8000/
```

---

## Tests

Este proyecto utiliza:

- PHPUnit para las pruebas automatizadas.

```bash
    php bin/phpunit
```

- PHPStan para verificar posibles errores estáticos y asegurar la calidad del código.

```bash
    php vendor/bin/phpstan analyse --configuration=phpstan.dist.neon > tests/phpstan_report.txt
```

---

## Licencia

Este proyecto está bajo la licencia [MIT](https://opensource.org/licenses/MIT). Consulta el archivo `LICENSE` para más información.

---