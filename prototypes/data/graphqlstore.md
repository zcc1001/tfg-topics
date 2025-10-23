[<p  align="center"><img src="./graphqlstore.png" alt="GraphQLStore CLI" width="300"></p>]()
# GraphQLStore

<div align="center">

[![PyPI version](https://badge.fury.io/py/graphqlstore.svg)](https://badge.fury.io/py/graphqlstore)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: Private](https://img.shields.io/badge/License-Private-red.svg)](LICENSE)
[![CI](https://github.com/adg1023/graphqlstore/actions/workflows/ci.yml/badge.svg)](https://github.com/adg1023/graphqlstore/actions/workflows/ci.yml)
[![CD](https://github.com/adg1023/graphqlstore/actions/workflows/cd.yml/badge.svg)](https://github.com/adg1023/graphqlstore/actions/workflows/cd.yml)
[![coverage](https://img.shields.io/badge/coverage-97%25-brightgreen.svg)](https://github.com/your-username/graphqlstore)
[![code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen.svg)](https://pre-commit.com)
[![pytest](https://img.shields.io/badge/pytest-8.3.5-brightgreen.svg)](https://docs.pytest.org/en/stable/)
[![rich](https://img.shields.io/badge/Rich-14.0.0-blue.svg)](https://rich.readthedocs.io/en/stable/introduction.html)

**🚀 Advanced CLI Tool to manage GraphQL Schemas and databases in a synchronized way.**

📖 Documentation • ⚡ Getting Started • 🎯 Features • 📊 Examples

</div>

---

## 🌟 Description

GraphQLStore CLI is a professional command-line tool that automates relational database management from GraphQL schemas. It transforms GraphQL definitions into fully functional database structures with support for complex relationships, automatic migrations, and rich visualization.

### ✨ ¿Why GraphQLStore CLI?

- 🔄 **Automatic Transformation**: Convert GraphQL schemas to MySQL/PostgreSQL without manual configuration 
- 🛡️ **Secure Migrations**: Evolve your database while preserving data integrity
- 🎨 **User-Friendly Visualization**: Friendly interface with Rich Console and syntax highlighting
- ⚡ **Intelligent Detection**: Automatically find and process schemas
- 🔗 **Advanced Relationships**: Full support for 1:1, N:1, 1:N, and N:M relationships
- 📊 **Production Ready**: 97% test coverage and scalable architecture

---

## 🎯 Features

### 🏗️ Main Commands

| Command | Description | Status |
|---------|-------------|--------|
| `conexion` | Configure connection to MySQL database | ✅  |
| `probar-conexion` | Check connectivity and diagnostics | ✅ |
| `inicializar` | Create database from GraphQL schema | ✅  |
| `migracion` | Evolve existing schemas | ✅ |

### 🔧 Technical Features

- **🔍 GraphQL Parser**: Comprehensive schema analysis
- **🔗 Relationship Processor**: Intelligent relationship handling
- **🗄️ MySQL Generator**: Optimized conversion GraphQL → SQL
- **🗄️ PostgreSQL Generator**: Optimized conversion GraphQL → SQL
- **📈 Migration System**: Safe evolution of schemas

### 🎨 Supported Data Types

| GraphQL | MySQL | Features |
|---------|-------|----------------|
| `ID` | `VARCHAR(25)` | Automatic primary keys |
| `String` | `VARCHAR(255)` | Full UTF-8 support |
| `Int` | `INT` | Integers |
| `Boolean` | `BOOLEAN` | True/false values |
| `DateTime` | `DATETIME` | Timestamps with @createdAt/@updatedAt |
| `Float` | `DECIMAL(10,2)` | Decimal precision |
| `JSON` | `JSON` | Native complex objects |
| `[]` | `JSON` | Lists of values |
| `Enum` | `ENUM(...)` | Type-safe enumerations |
| `!` | `NOT NULL` | Required field validation |
| sin `!` | `NULL` | Optional fields |

### 📜 Supported Directives
| Directive | Description | Arguments |
|-----------|-------------|-----------|
| `@id` | Define a field as primary key | None |
| `@unique` | Ensure the field is unique | None |
| `@default` | Set a default value for the field | `value` |
| `@db` | Rename the field in the database | `rename` |
| `@protected` | Hide the field in the client schema | None |
| `@relation` | Define relationships between types | `name`, `type`, `onDelete` |
| `@createdAt` | Mark the field with the creation date | None |
| `@updatedAt` | Mark the field with the update date | None |

#### Directive @id - Primary Key
The `@id` directive defines a field as a primary key in the database:

**Syntax**:
```graphql
id: ID! @id
```

**Example**:
```graphql
type User {
  id: ID! @id
  nombre: String!
}
```

**Generated SQL**:
```sql
CREATE TABLE User (
  id VARCHAR(25) NOT NULL PRIMARY KEY,
  nombre VARCHAR(255) NOT NULL
);
```

#### Directive @unique - Unique Fields
The `@unique` directive ensures that a scalar field has unique values in the database:

**Syntax**:
```graphql
campo: Tipo! @unique
```

#### Directive @default - Default Values
The `@default` directive allows setting default values for scalar fields:

**Syntax**:
```graphql
campo: Tipo! @default(value: "valor_por_defecto")
```

**Examples**:
```graphql
type User {
  active: Boolean! @default(value: "true")
  age: Int! @default(value: 18)
  role: UserRole! @default(value: "ADMIN")
}
```

**Generated SQL**:
```sql
CREATE TABLE User (
  active BOOLEAN NOT NULL DEFAULT true,
  age INT NOT NULL DEFAULT 18,
  role ENUM('ADMIN', 'AUTHOR', 'USER') NOT NULL DEFAULT 'ADMIN'
);
```

#### Directive @db - Column Renaming

The `@db` directive allows using different names between GraphQL and the database:

**Syntax**:
```graphql
campo: Tipo! @db(rename: "nombre_columna_sql")
```

**Examples**:
```graphql
type User {
   fullName: String! @db(rename: "full_name")
   email: String! @db(rename: "email_address")
   phone: String @db(rename: "phone_number")
}
```

**Generated SQL**:
```sql
CREATE TABLE User (
  full_name VARCHAR(255) NOT NULL,
  email_address VARCHAR(255) NOT NULL,
  phone_number VARCHAR(255)
);
```

#### Directive @relation - Advanced Relationships

The `@relation` directive manages complex relationships between types with granular control:

**Syntax**:
```graphql
campo: [Tipo] @relation(name: "NombreRelacion", type: TIPO_RELACION, onDelete: ACCION)
```

**Arguments**:
- `name`: unique name of the relationship (required for all relationships)
- `type`: Type of physical relationship
  - `INLINE`: Optional for 1:1, N:1, and 1:N relationships (foreign key)
  - `TABLA`: Required for N:M relationships (junction table)
- `onDelete`: Action when deleting parent record
  - `CASCADE`: Cascade deletion (deletes child records)
  - `SET_NULL`: Sets NULL on child records (does not delete)

**Examples of N:1 relationships with INLINE**:
```graphql
type User {
   id: ID! @id
   email: String! @unique
   posts: [Post] @relation(name: "UserPosts")
}

type Post {
   id: ID! @id
   title: String!
   author: User! @relation(name: "UserPosts", onDelete: CASCADE)
}
```

**Generated SQL for N:1**:
```sql
-- Tabla User
CREATE TABLE User (
   id VARCHAR(25) NOT NULL PRIMARY KEY,
   email VARCHAR(255) NOT NULL UNIQUE
   );

-- Tabla Post con clave foránea
CREATE TABLE Post (
   id VARCHAR(25) NOT NULL PRIMARY KEY,
   author_id VARCHAR(25) NOT NULL,
   FOREIGN KEY (author_id) REFERENCES User(id) ON DELETE CASCADE
);
```

**Examples of 1:N relationships with INLINE**:
```graphql
type Product {
   id: ID! @id
   name: String!
   productType: ProductType! @relation(name: "ProductTypeProducts", onDelete: CASCADE)
}

type ProductType {
   id: ID! @id
   name: String! @unique
   products: [Product] @relation(name: "ProductTypeProducts", onDelete: CASCADE)
}
```

**Generated SQL for 1:N**:
```sql
-- Tabla ProductType
CREATE TABLE ProductType (
   id VARCHAR(25) NOT NULL PRIMARY KEY,
   name VARCHAR(255) NOT NULL
);

-- Tabla Product con clave foránea
CREATE TABLE Product (
   id VARCHAR(25) NOT NULL PRIMARY KEY,
   name VARCHAR(255) NOT NULL,
   product_type_id VARCHAR(25) NOT NULL,
   FOREIGN KEY (product_type_id) REFERENCES ProductType(id) ON DELETE CASCADE
);
```


**Examples of N:M relationships with TABLE**:
```graphql
type Post {
   id: ID! @id
   title: String!
   tags: [Tag] @relation(name: "PostTags", type: TABLE, onDelete: CASCADE)
}

type Tag {
   id: ID! @id
   name: String! @unique
   posts: [Post] @relation(name: "PostTags", type: TABLE, onDelete: CASCADE)
}
```

**Generated SQL for N:M**:
```sql
-- Tabla Post
CREATE TABLE Post (
   id VARCHAR(25) NOT NULL PRIMARY KEY,
   title VARCHAR(255) NOT NULL
);

-- Tabla Tag
CREATE TABLE Tag (
   id VARCHAR(25) NOT NULL PRIMARY KEY,
   name VARCHAR(255) NOT NULL UNIQUE
);

-- Tabla intermedia PostTags
CREATE TABLE PostTags (
   post_id VARCHAR(25) NOT NULL,
   tag_id VARCHAR(25) NOT NULL,
   PRIMARY KEY (post_id, tag_id),
   FOREIGN KEY (post_id) REFERENCES Post(id) ON DELETE CASCADE,
   FOREIGN KEY (tag_id) REFERENCES Tag(id) ON DELETE CASCADE
);
```

---

## ⚡ Getting Started

### 📦 Installation

#### From PyPI (Recommended)
```bash
pip install graphqlstore
```

#### From Source Code
```bash
git clone https://github.com/your-username/graphqlstore.git
cd graphqlstore
pipenv install --dev
```

### 🚀 Basic Workflow

#### 1. **Configure Connection**
```bash
# Interactive setup
graphqlstore conexion

# or direct connection with parameters
graphqlstore conexion \
  --host localhost \
  --puerto 3306 \
  --usuario admin \
  --password secret \
  --base-datos mi_app
```

#### 2. **Verify Connection**
```bash
graphqlstore probar-conexion --verbose
```

#### 3. **Design GraphQL Schema**
```graphq
type User {
   id: ID! @id
   username: String!
   email: String! @unique
}
```

#### 3. **Initialize Database**
```bash
# From specific file
# NOTE: It is necessary to specify the schema if there are multiple .graphql files
# in the current directory
graphqlstore inicializar --esquema schema.graphql

# Automatic detection
graphqlstore inicializar
```

#### 4. **Evolve Schema**
```bash
# Automatic migration
# NOTE: It is necessary to specify the schema if there are multiple .graphql files
# in the current directory
graphqlstore migracion --esquema schema.graphql
```

## 📊 Examples

### 🎮 Example GraphQL Schema

```graphql
scalar Json
scalar DateTime

type User {
  id: ID! @id
  username: String! @unique
  email: String! @unique
  role: UserRole!
  posts: [Post!]! @relation(name: "UserPosts")
  profile: Profile @relation(name: "UserProfile")
  createdAt: DateTime @createdAt
  updatedAt: DateTime @updatedAt
}

type Post {
  id: ID! @id
  title: String!
  content: String
  published: Boolean! @default(value: "false")
  tags: [String!]!
  author: User! @relation(name: "UserPosts", onDelete: CASCADE)
  createdAt: DateTime @createdAt
}

type Profile {
  id: ID! @id
  bio: String
  avatar: String
  user: User! @relation(name: "UserProfile", onDelete: CASCADE)
}

enum UserRole {
  ADMIN
  AUTHOR
  USER
}
```

### 🗄️ Automatically Generated SQL

```sql
-- Tabla User con constraints
CREATE TABLE User (
  `id` VARCHAR(25) NOT NULL PRIMARY KEY,
  `username` VARCHAR(255) NOT NULL,
  `email` VARCHAR(255) NOT NULL,
  `role` ENUM('ADMIN','AUTHOR','USER') NOT NULL,
  `createdAt` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updatedAt` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY `uk_username` (`username`),
  UNIQUE KEY `uk_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Relaciones con foreign keys
ALTER TABLE `Post`
ADD COLUMN `author_id` VARCHAR(25) NOT NULL,
ADD CONSTRAINT `fk_User_posts_Post` FOREIGN KEY (`author_id`) 
REFERENCES `User`(id) ON DELETE CASCADE;

ALTER TABLE `Profile`
ADD COLUMN `user_id` VARCHAR(25) UNIQUE,
ADD CONSTRAINT `fk_User_profile_Profile` FOREIGN KEY (`user_id`) 
REFERENCES `User`(id) ON DELETE CASCADE;
```

### 📈 Friendly Visualization

```bash
GraphQLStore CLI v3.0.0
Desplegando servicio

📋 Diferencias detectadas
├── ➕ Tablas agregadas: 1
├── 🔹 Campos agregados: 3
└── 🔗 Relaciones agregadas: 2

🔧 CREAR TABLA
├── Creando tabla Profile

🔧 AGREGAR RELACIÓN
├── Agregando relación UserProfile

✅ Migración generada exitosamente
📊 Total de sentencias SQL: 5
```

---

## 🏗️ Architecture

### 📁 Project Structure

```
graphqlstore/
├── 📂 source/cli/
│   ├── 🔌 conexion/          # Manage database configuration
│   ├── 🩺 probar_conexion/   # Diagnostics and validation
│   ├── 🚀 inicializar/       # Schema initialization
│   ├── 📈 migracion/         # Migration system
│   ├── 🔍 graphql/           # GraphQL engine
│   │   ├── parser.py         # Schema parser
│   │   ├── mysql_generador.py # SQL generator
│   │   ├── mysql_migracion.py # Migration engine
│   │   └── procesar_relaciones.py # Relations processor
│   ├── 🗄️ database/         # Database adapters
│   └── 🛠️ utilidades/       # Utility tools
├── 📂 tests/                 # Test suite (97% coverage)
└── 📂 .github/workflows/     # Automated CI/CD
├── 📄 README.md              # Main documentation
├── 📄 LICENSE                # Project license
├── 📄 setup.py               # Package configuration
├── 📄 requirements.txt       # Project dependencies
├── 📄 requirements-dev.txt   # Development dependencies
├── 📄 .pre-commit-config.yaml # Pre-commit configuration
├── 📄 Pipfile                # Dependency management with Pipenv
├── 📄 pyproject.toml         # Project configuration
├── 📄 .pylintrc              # Pylint configuration
```

### 🔧 Main Components

#### 🔍 **GraphQL Parser** ([`source/cli/graphql/docs/parser.md`](source/cli/graphql/docs/parser.md))
- Schema analysis
- Extraction of types, fields, and directives
- Syntax and semantic validation

#### 🔗 **Relations Processor** ([`source/cli/graphql/docs/procesar_relaciones.md`](source/cli/graphql/docs/procesar_relaciones.md))
- Automatic relationship detection
- Classification 1:1, 1:N, N:M
- Constraint generation

#### 🗄️ ****MySQL Generator** ([`source/cli/graphql/docs/mysql_generador.md`](source/cli/graphql/docs/mysql_generador.md))
- GraphQL → SQL transformation
- Complete DDL generation

#### 📈 **Migration System** ([`source/cli/graphql/docs/mysql_migracion.md`](source/cli/graphql/docs/mysql_migracion.md))
- Intelligent change detection
- Incremental SQL generation
- Referential integrity preservation

---

## 🛠️ Development Environment

### 📋 Requirements
- **Python**: 3.10+
- **MySQL**: 8.0+
- **Pipenv**: For dependency management

### 🔧 Quality Tools

| Tool | Purpose | Status |
|------|---------|--------|
| **pytest** | Testing framework | ✅ 97% coverage |
| **black** | Code formatting | ✅ Configured |
| **flake8** | Linting (lightweight) | ✅ Configured |
| **pylint** | Linting (exhaustive) | ✅ Configured |
| **mypy** | Type checking | ✅ Configured |
| **pre-commit** | Git hooks | ✅ Configured |


## 📊 Coverage and Quality

### 🎯 Coverage Metrics

| MModule | Statements | Miss | Branch | BrPart | Cover |
|--------|------------|------|--------|--------|-------|
| **Parser GraphQL** | 67 | 1 | 18 | 1 | **98%** |
| **Procesador Relaciones** | 96 | 4 | 38 | 6 | **93%** |
| **Generador MySQL** | 237 | 5 | 94 | 11 | **95%** |
| **Sistema Migraciones** | 396 | 17 | 208 | 23 | **93%** |
| **Comandos CLI** | 271 | 11 | 52 | 3 | **100%** |
| **🎯 TOTAL PROYECTO** | **4860** | **88** | **702** | **85** | **🏆 97%** |

### ✅ Test Suite (TOTAL PROJECT)

- **📈 234 tests** running in **4.54 seconds**
- **🎯 97% global coverage** with **0 failures**
- **🔍 Edge cases** and **full integration**
- **🚀 Automated CI/CD** on GitHub Actions

---

## 🔄 CI/CD Pipeline

### 🛠️ Automatized Workflow

### 🔍 **CI Pipeline** (`.github/workflows/ci.yml`)

**🔄 Continuous Integration Flow:**

```
📋 Input (Push/PR)
   ↓
🔧 Dependency Installation
   ↓
🎯 Pre-commit Hooks
   ├── ⚫ Black (Code formatting)
   ├── 🔍 Flake8 (Lightweight linting)
   ├── 📋 Pylint (Exhaustive analysis)
   └── 🔤 Mypy (Type checking)
   ↓
🧪 Testing Suite + Coverage
   ↓
✅ Complete Pipeline
```

| Stage | Process | Status |
|-------|---------|--------|
| **🔧 Setup** | Dependency installation | ✅ |
| **🎯 Quality** | Complete pre-commit hooks | ✅ |
| **⚫ Black** | Automatic code formatting | ✅ |
| **🔍 Flake8** | Lightweight and fast linting | ✅ |
| **📋 Pylint** | Exhaustive code analysis | ✅ |
| **🔤 Mypy** | Static type checking | ✅ |
| **🧪 Testing** | Complete suite with coverage | ✅ |

### 🚀 **CD Pipeline** (`.github/workflows/cd.yml`)

**📦 Continuous Deployment Flow:**

```
🏷️ Release Tag
   ↓
🛠️ Build Tools Configuration
   ↓
📦 Multi-format Packaging
   ├── 🎯 Wheel Distribution
   └── 📄 Source Distribution
   ↓
🚀 Publish to PyPI
   ↓
📋 GitHub Release + Artifacts
   ↓
✅ Complete Deploy
```

| Stage | Process | Description |
|-------|---------|-------------|
| **🛠️ Setup** | Tools configuration | Preparation of the build environment |
| **📦 Build** | Multi-format packaging | Wheel + Source distributions |
| **🎯 Wheel** | Binary distribution | Optimized fast installation |
| **📄 Source** | Source distribution | Maximum compatibility |
| **🚀 PyPI** | Automatic publication | Deploy in new versions |
| **📋 GitHub** | Release + artifacts | Documentation and files |

### ⚡ **Pipeline Triggers**
- **CI**: `push`, `pull_request` → `main`
- **CD**: `release` → `published` → PyPI + GitHub Release

### 📦 Releases

| Version | Status | Features |
|---------|--------|----------------|
| **v0.x.0** | ✅ | Correct Deployment |
| **v1.0.0** | ✅ | Complete Core |
| **v2.0.0** | ✅ | Advanced Directives |
| **v3.0.0** | ✅ | Template generator of GraphQL server in JS |
| **v3.x.0** | ✅ | Bugs, improves and documentation |
| **v4.0.0** | 🎯 **Current** | Refactorization, implementation of new design patterns and support multi-database (PostgreSQL) |
---

## 📚 Documentation

### 📖 Detailed Guides

- 🔌 **[Command `conexion`](source/cli/conexion/README_latest.md)** - Database configuration
- 🩺 **[Command `probar-conexion`](source/cli/probar_conexion/README.md)** - Diagnostics and database validation
- 🚀 **[Command `inicializar`](source/cli/inicializar/README.md)** - Initialization of schemas
- 📈 **[Command `migracion`](source/cli/migracion/README.md)** - Migration system
- 🔍 **[Command `servidor`](source/cli/servidor/README.md)** - GraphQL server generator in JavaScript

### 🔧 Technical Documentation

- 🔍 **[Parser GraphQL](source/cli/graphql/docs/parser.md)** - Parsing engine
- 🔗 **[Relationship Processor](source/cli/graphql/docs/procesar_relaciones.md)** - Relationship management
- 🗄️ **[MySQL Generator](source/cli/graphql/docs/mysql_generador.md)** - SQL transformation
- 📈 **[Migration System](source/cli/graphql/docs/mysql_migracion.md)** - Schema evolution

---

## 🎯 Use Cases

### 🚀 **API Development**
```bash
# Complete project initialization
graphqlstore conexion
graphqlstore inicializar
# ✅ Database ready for development
```

### 🔄 **Evolution of Schemas**
```bash
# Automatic migration
graphqlstore migracion
# ✅ Schema updated preserving data (from existing tables and relationships)
```

### 🏭 **Integration CI/CD**
```bash
# Silent mode for pipelines
graphqlstore migracion \
  --esquema schemas/production.graphql \
  --no-visualizar-salida \
  --no-visualizar-sql
```

---

## 🤝 Contribute

### 🐛 Report Issues

### Coming Soon

### 📝 Local Development

### Coming Soon

---

## 🗺️ Roadmap

### 🚀 **v1.0.0** - Core
- [x] `conexion` - Configure connection to MySQL
- [x] `probar-conexion` - Connectivity verification
- [x] `inicializar` - Database initialization from GraphQL schema
- [x] `migracion` - Automatic migration system

### 🎯 **v2.0.0** - Advanced Directives
- [x] `@unique` - Unique fields
- [x] `@default` - Default values
- [x] `@db` - Field renaming
- [x] `@protected` - Protected fields

### 🚀 **v3.0.0** - GraphQL Server
- [x]  `server` - Generate GraphQL server structure in JavaScript

### 🏭 **v3.x.0** - Bugs, improvements and documentation
- [x] Fix bugs and improve performance
- [x] Enhance the workflow of the connection command
- [x] Improve core functionalities
- [x] Add documentation for the `server` command
- [x] Improve all documentation
- [x] Improve the implementation of the GraphQL.js server

### 🏭 **v4.0.0** - Multi-Database
- [x] Refactor `GeneradorEsquemaMySQL` and `GenerarMigracionMySQL` modules implementing design patterns to scale the code and improve maintainability, especially to implement multi-database functionality.
- [x] Implement PostgreSQL support
---


## 📜 License

This project uses a **Open Source License - Apache 2.0**.

See LICENSE for full details.

---

<div align="center">

### 🚀 **¡Transform your GraphQL schemas into relational databases with a single command!**

[![Get Started](https://img.shields.io/badge/Get%20Started-brightgreen?style=for-the-badge&logo=rocket)](https://pypi.org/project/graphqlstore/)
[![Documentation](https://img.shields.io/badge/Documentation-blue?style=for-the-badge&logo=book)](source/cli/)
[![GitHub](https://img.shields.io/badge/GitHub-black?style=for-the-badge&logo=github)](https://github.com/adg1023/graphqlstore)

---

**📧 Questions?** • **🐛 Issues?** • **💡 Ideas?**

COMING SOON

</div>