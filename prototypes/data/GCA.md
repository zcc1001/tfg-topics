# GCA  
![license](https://img.shields.io/badge/Apache%202.0-4D4D4D?style=flat-square&logo=apache&logoColor=white)

GCA is a centralized platform designed to manage and control classrooms efficiently. 
It provides a unified system to handle configurations, command templates, and access restrictions across multiple 
devices in educational centers. Built with a Spring Boot backend API and a Python client application, GCA ensures 
seamless communication and dynamic management of classroom resources, improving operational control and security.

## Features

- **Centralized Management**: Unified control over classroom devices and configurations.
- **Dynamic Command Execution**: Execute commands on devices in real-time.
- **Configuration Management**: Handle device configurations and command templates efficiently.
- **User-Friendly Interface**: Intuitive web interface for easy navigation and management.
- **Easy Deployment**: Docker-based deployment for quick setup and scalability.

## Stack
-  ![spring](https://img.shields.io/badge/Spring%20Boot-6DB33F?style=flat-square&logo=spring&logoColor=white)
- ![python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
- ![angular](https://img.shields.io/badge/Angular-DD0031?style=flat-square&logo=angular&logoColor=white)
- ![docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
## Deployment


## Installation

1. Clone the repository:
    ```bash
   git clone https://github.com/rmg1008/GCA.git
   cd GCA
    ```
2. Build and start all the services:
    ```bash
    docker-compose up --build
    ```

## Services

| Service    | Technology       | URL / Port               |
|------------|------------------|--------------------------|
| Frontend   | Angular + Nginx  | [http://localhost:4200]  |
| Backend    | Spring Boot      | [http://localhost:8080]  |
| Database   | MariaDB          | `localhost:3306`         |