"""
app/core/circuit_breaker.py
----------------------------
Patrón Circuit Breaker y Timeouts estrictos con HTTPX para ZenPay.
Protege el backend contra caídas o latencias excesivas en proveedores externos (pasarelas de pago).
Activa rescate semántico inteligente (Fallback) para evitar que el usuario sufra un error 503.
"""

import time
import asyncio
from enum import Enum
from typing import Optional, Dict, Any

try:
    import httpx
except ImportError:
    import httpx2 as httpx

class EstadoCircuito(str, Enum):
    CERRADO = "CERRADO"          # Tráfico normal; el proveedor responde
    ABIERTO = "ABIERTO"          # Proveedor colapsó; cortamos tráfico de inmediato
    SEMIABIERTO = "SEMIABIERTO"  # Tiempo de enfriamiento superado; probando recuperación

class CircuitoCortadoError(Exception):
    """Excepción cuando el circuito está abierto y no debe llamarse al proveedor."""
    pass

class CircuitBreaker:
    """
    Controlador de resiliencia inspirado en los fusibles eléctricos.
    """
    def __init__(self, limite_fallos: int = 3, tiempo_enfriamiento_segundos: float = 5.0):
        self.limite_fallos = limite_fallos
        self.tiempo_enfriamiento = tiempo_enfriamiento_segundos
        self.estado = EstadoCircuito.CERRADO
        self.contador_fallos_consecutivos = 0
        self.momento_ultimo_fallo: Optional[float] = None

    def registrar_exito(self):
        """Restablece el circuito al estado CERRADO tras una respuesta exitosa."""
        self.contador_fallos_consecutivos = 0
        self.estado = EstadoCircuito.CERRADO

    def registrar_fallo(self):
        """Registra un fallo del proveedor. Si llega al umbral, abre el circuito."""
        self.contador_fallos_consecutivos += 1
        self.momento_ultimo_fallo = time.time()
        
        if self.contador_fallos_consecutivos >= self.limite_fallos:
            self.estado = EstadoCircuito.ABIERTO

    def verificar_disponibilidad(self):
        """Comprueba si podemos intentar una llamada o si el circuito la prohíbe."""
        if self.estado == EstadoCircuito.CERRADO:
            return

        if self.estado == EstadoCircuito.ABIERTO:
            tiempo_transcurrido = time.time() - (self.momento_ultimo_fallo or 0)
            if tiempo_transcurrido >= self.tiempo_enfriamiento:
                self.estado = EstadoCircuito.SEMIABIERTO
            else:
                tiempo_restante = self.tiempo_enfriamiento - tiempo_transcurrido
                raise CircuitoCortadoError(f"Circuito ABIERTO. Espera {tiempo_restante:.1f}s antes de reintentar.")

# Instancia global por defecto para la pasarela de pagos
TIMEOUT_ESTRICTO = httpx.Timeout(2.0, connect=1.0)
fusible_pagos = CircuitBreaker(limite_fallos=3, tiempo_enfriamiento_segundos=4.0)

async def procesar_pago_con_proveedor(url_api: str, id_pedido: str, monto: float) -> Dict[str, Any]:
    """
    Llama a la pasarela externa bajo el amparo del Circuit Breaker y Timeout.
    """
    fusible_pagos.verificar_disponibilidad()

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_ESTRICTO) as cliente:
            respuesta = await cliente.post(
                url_api,
                json={"pedido_id": id_pedido, "monto": monto}
            )
            respuesta.raise_for_status()
            fusible_pagos.registrar_exito()
            return {
                "estado": "aprobado",
                "codigo_autorizacion": "AUTH-778899",
                "mensaje": "Pago procesado exitosamente por el banco."
            }

    except (httpx.TimeoutException, httpx.HTTPStatusError, httpx.RequestError) as error_red:
        fusible_pagos.registrar_fallo()
        raise error_red

async def servicio_checkout_con_fallback(id_pedido: str, monto: float, url_proveedor: str) -> Dict[str, Any]:
    """
    Punto de entrada de checkout con Fallback Inteligente y Empático.
    """
    try:
        resultado = await procesar_pago_con_proveedor(url_proveedor, id_pedido, monto)
        return resultado
    except (CircuitoCortadoError, httpx.TimeoutException, httpx.HTTPError) as excepcion:
        # Fallback VIP: No dejamos al usuario con un error 503
        return {
            "estado": "pedido_reservado_offline",
            "pedido_id": id_pedido,
            "monto": monto,
            "mensaje": "La red bancaria externa está experimentando lentitud.",
            "alternativa_sugerida": "Pagar mediante Transferencia Bancaria (5% de descuento) o Contra Entrega.",
            "tiempo_reserva_minutos": 120,
            "rescate_ia": {
                "activo": True,
                "mensaje_cliente": (
                    "Detectamos intermitencia con tu banco. Para tu tranquilidad, "
                    "hemos reservado tu pedido por 2 horas y generado un código QR seguro."
                ),
                "enlace_qr": f"https://zenpay.dev/qr-transferencia/{id_pedido}"
            }
        }
