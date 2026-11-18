# 🐍 Código Fuente: Problema #03 — Resiliencia con HTTPX & Circuit Breaker
`zenpay-fastapi-backend/circuit_breaker/`

Este directorio contiene la implementación real en Python del caso empresarial presentado en el video: **cómo evitar que una tienda o sistema colapse cuando una pasarela de pagos o proveedor externo se cae**.

---

## 📁 Archivos en este Directorio

* **`cliente_inseguro.py`**: El antipatrón común. Hace peticiones a proveedores externos sin timeout explícito, lo que provocaría que el servidor se quede colgado durante minutos esperando.
* **`cliente_zen_circuit_breaker.py`**: La solución profesional. Implementa:
  1. Timeouts asíncronos estrictos con `httpx`.
  2. Una máquina de estados limpia de **Circuit Breaker** (*Cerrado, Abierto, Semiabierto*).
  3. Mecanismo de contingencia y **Rescate con IA (Fallback Semántico)** para que el cliente reciba un trato VIP (reserva de pedido + código QR) en vez de un error seco 503.
* **`test_circuit_breaker.py`**: Suite de pruebas automatizadas con **Pytest** que simula caídas de red y verifica que el fusible se active correctamente.

---

## 🚀 Cómo Probar el Código en tu Computadora

### 1. Instalar dependencias
Asegúrate de tener instaladas las librerías necesarias:
```bash
pip install httpx pytest pytest-asyncio
```

### 2. Ejecutar la solución Zen
```bash
python cliente_zen_circuit_breaker.py
```
Verás en la consola cómo se comporta el sistema cuando el proveedor responde, cuando empieza a fallar y cómo salta el **Circuit Breaker** para proteger el sistema.

### 3. Ejecutar las pruebas automáticas con Pytest
```bash
pytest test_circuit_breaker.py -v
```
Todas las pruebas deben pasar en verde (🟢 PASS), validando la resiliencia del software.
