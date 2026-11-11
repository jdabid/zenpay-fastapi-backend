# 🍵 ZenPay Backend API — Enterprise Resilience Architecture 🚀💳

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2.6+-E92063.svg?style=flat&logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-D71F00.svg?style=flat&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Pytest](https://img.shields.io/badge/Pytest-100%25_Passing-0A9EDC.svg?style=flat&logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue.svg?logo=python&logoColor=white)](https://www.python.org/)

> **Canal Oficial:** [@capyzendev](https://www.youtube.com/@capyzendev)  
> *«Aprende a programar manteniendo la paz. Sin estrés, sin bugs.»*  
> **Propósito:** Arquitectura de backend corporativa para procesamiento de órdenes y pagos blindada contra caídas en producción y errores 500 no controlados.

---

## 🎯 1. ¿Por qué existe este proyecto?

El 80% de las caídas de sistemas en e-commerce y pasarelas de pago ocurren un viernes por la tarde debido a **errores 500 no controlados** (divisiones por cero, claves inexistentes, datos corruptos no tipados).

**ZenPay** demuestra la arquitectura que aplican los ingenieros Backend y QA Senior:
1. **Tipado y Validación Estricta en la Puerta de Entrada:** Con **Pydantic v2**, ningún dato malformado cruza la frontera de los controladores.
2. **Excepciones Semánticas HTTP:** Desacoplamiento de errores de cliente (`400 Bad Request`, `404 Not Found`, `422 Unprocessable Content`).
3. **Escudo Global de Excepciones:** Si ocurre un imprevisto, el middleware global atrapa la excepción, genera un `Trace ID` único para auditoría en logs y devuelve un JSON elegante sin tumbar el servidor Uvicorn.
4. **QA Automation Industrial:** 100% de cobertura en flujos críticos con **Pytest** y **TestClient** sobre base de datos en memoria (`sqlite:///:memory:`).

---

## 🏛️ 2. Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       ARQUITECTURA DEFENSIVA DE ZENPAY                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  Cliente Web / Móvil   ➔  Pydantic v2 (Validación Estricta)                 │
│  Swagger UI (/docs)    ➔  FastAPI Routers (/api/v1/pedidos)                 │
│  Pytest (TestClient)   ➔  Escudo Global (@app.exception_handler)            │
│                        ➔  SQLAlchemy 2.0 ORM  ➔  SQLite / PostgreSQL        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 💻 3. Tech Stack

| Componente | Tecnología | Rol |
| :--- | :--- | :--- |
| **Framework Web** | FastAPI 0.110+ | Enrutamiento de alto rendimiento ASGI |
| **Validación de Datos** | Pydantic v2 | Schemas tipados y coerción de tipos |
| **Persistencia ORM** | SQLAlchemy 2.0 | Modelos relacionales desacoplados |
| **Testing & QA** | Pytest + TestClient (HTTPX) | Pruebas de integración automatizadas |
| **Documentación** | Swagger UI & OpenAPI | Contrato interactivo en `/docs` |
| **Contenedorización** | Docker + Docker Compose | Despliegue reproducible multiplataforma |
| **CI/CD** | GitHub Actions | Pipeline automatizado de linting y tests |

---

## 📁 4. Estructura del Repositorio

```
zenpay-fastapi-backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── health.py           # Health check endpoint
│   │       │   └── pedidos.py          # CRUD de pedidos y lógica de pagos
│   │       └── api.py                  # Agregador de routers v1
│   ├── core/
│   │   ├── config.py                   # Configuración con pydantic-settings
│   │   └── exceptions.py               # Escudos globales y manejo de errores 500
│   ├── database/
│   │   └── connection.py               # Sesiones de base de datos SQLAlchemy
│   ├── models/
│   │   └── pedido.py                   # Entidades de base de datos
│   ├── schemas/
│   │   └── pedido.py                   # Contratos DTO de entrada y salida
│   └── main.py                         # Instancia central de FastAPI
├── tests/
│   ├── conftest.py                     # Fixtures aisladas en memoria para Pytest
│   ├── test_pedidos.py                 # Tests de endpoints y reglas de negocio
│   └── test_resiliencia.py             # Pruebas del Escudo Global (Cero caídas 500)
├── .github/workflows/
│   └── ci.yml                          # GitHub Actions CI Workflow
├── Dockerfile                          # Multi-stage production container
├── docker-compose.yml                  # Orquestación local en un comando
├── requirements.txt                    # Dependencias de producción y pruebas
├── .env.example                        # Variables de entorno seguras
└── README.md                           # Documentación técnica maestra
```

---

## 🚀 5. Inicio Rápido (3 Comandos)

### 1. Clonar el repositorio y entrar
```bash
git clone https://github.com/capyzendev/zenpay-fastapi-backend.git
cd zenpay-fastapi-backend
```

### 2. Crear entorno virtual e instalar dependencias
```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Iniciar el servidor de desarrollo
```bash
uvicorn app.main:app --reload
```

Abre tu navegador en:
* 🌐 **Swagger UI Interactiva:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* 📖 **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
* 🩺 **Health Check:** [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)

---

## 🧪 6. Ejecutar la Suite de Pruebas (QA Automation)

Ejecuta las pruebas unitarias y de integración automáticas con reporte de cobertura:

```bash
pytest tests/ -v
```

Salida esperada:
```text
tests/test_pedidos.py::test_root_endpoint PASSED                         [ 10%]
tests/test_pedidos.py::test_health_check_endpoint PASSED                  [ 20%]
tests/test_pedidos.py::test_crear_pedido_valido_status_201 PASSED        [ 30%]
tests/test_pedidos.py::test_crear_pedido_monto_negativo_falla_422 PASSED  [ 40%]
tests/test_pedidos.py::test_obtener_pedido_existente_status_200 PASSED    [ 50%]
tests/test_pedidos.py::test_obtener_pedido_inexistente_retorna_404 PASSED [ 60%]
tests/test_pedidos.py::test_descuento_promedio_con_cupones_status_200 PASSED [ 70%]
tests/test_pedidos.py::test_descuento_promedio_cero_cupones_retorna_400 PASSED [ 80%]
tests/test_resiliencia.py::test_escudo_global_atrapa_error_500_con_trace_id PASSED [ 90%]
tests/test_resiliencia.py::test_servidor_sigue_vivo_despues_de_un_error_500 PASSED [100%]

======================== 10 passed in 0.08s ========================
```

---

## 🐳 7. Ejecución con Docker

Si prefieres correrlo en un contenedor sin instalar Python en tu máquina local:

```bash
docker-compose up --build
```

---

## 📄 Licencia

Este proyecto está distribuido bajo la licencia **MIT**. Siéntete libre de utilizarlo como plantilla base para tus proyectos o como proyecto estrella en tu portafolio de LinkedIn.

---

> Creado con serenidad por **Capyzen** ([@capyzendev](https://www.youtube.com/@capyzendev)).  
> *«Aprende a programar manteniendo la paz.»* 🍵
