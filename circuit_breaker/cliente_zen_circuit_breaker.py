"""
cliente_zen_circuit_breaker.py
------------------------------
Solución defensiva y resiliente de nivel Backend Senior:
Implementación del patrón Circuit Breaker y Timeouts estrictos con HTTPX.

Garantiza que la caída o lentitud de un proveedor externo (pasarela de pagos)
nunca paralice la aplicación principal, activando un plan de contingencia (Fallback).
"""

import time
import asyncio
from enum import Enum
from typing import Callable, Any, Optional

try:
    import httpx
except ImportError:
    import httpx2 as httpx

class EstadoCircuito(str, Enum):
    CERRADO = "CERRADO"          # Todo funciona bien; el tráfico fluye normalmente
    ABIERTO = "ABIERTO"          # El proveedor falló repetidamente; bloqueamos llamadas
    SEMIABIERTO = "SEMIABIERTO"  # Tiempo de enfriamiento cumplido; probamos si ya revivió

class CircuitoCortadoError(Exception):
    """Excepción lanzada cuando el circuito está abierto y no debe llamarse al proveedor."""
    pass

class CircuitBreaker:
    """
    Controlador de resiliencia inspirado en los fusibles eléctricos del hogar.
    """
    def __init__(self, limite_fallos: int = 3, tiempo_enfriamiento_segundos: float = 5.0):
        self.limite_fallos = limite_fallos
        self.tiempo_enfriamiento = tiempo_enfriamiento_segundos
        self.estado = EstadoCircuito.CERRADO
        self.contador_fallos_consecutivos = 0
        self.momento_ultimo_fallo: Optional[float] = None

    def registrar_exito(self):
        """Si la llamada tuvo éxito, restauramos la paz del circuito."""
        self.contador_fallos_consecutivos = 0
        self.estado = EstadoCircuito.CERRADO

    def registrar_fallo(self):
        """Registra un tropiezo del proveedor. Si llega al límite, abre el circuito."""
        self.contador_fallos_consecutivos += 1
        self.momento_ultimo_fallo = time.time()
        
        if self.contador_fallos_consecutivos >= self.limite_fallos:
            self.estado = EstadoCircuito.ABIERTO
            print(f"\n⚡ [CIRCUIT BREAKER] ¡Límite de {self.limite_fallos} fallos alcanzado! Circuito ABIERTO. Cortando tráfico.")

    def verificar_disponibilidad(self):
        """Comprueba si podemos intentar una llamada o si el circuito la prohíbe."""
        if self.estado == EstadoCircuito.CERRADO:
            return

        if self.estado == EstadoCircuito.ABIERTO:
            tiempo_transcurrido = time.time() - (self.momento_ultimo_fallo or 0)
            if tiempo_transcurrido >= self.tiempo_enfriamiento:
                self.estado = EstadoCircuito.SEMIABIERTO
                print(f"\n🔄 [CIRCUIT BREAKER] Tiempo de enfriamiento superado ({tiempo_transcurrido:.1f}s). Estado: SEMIABIERTO (probando servicio).")
            else:
                tiempo_restante = self.tiempo_enfriamiento - tiempo_transcurrido
                raise CircuitoCortadoError(f"Circuito ABIERTO. Espera {tiempo_restante:.1f}s antes de reintentar.")

# 1. Definimos un Timeout estricto de empresa: 2.0s de espera máxima
TIMEOUT_ESTRICTO = httpx.Timeout(2.0, connect=1.0)
fusible_pagos = CircuitBreaker(limite_fallos=3, tiempo_enfriamiento_segundos=4.0)

async def procesar_pago_con_proveedor(url_api: str, id_pedido: str, monto: float) -> dict:
    """
    Llama a la pasarela externa bajo el amparo del Circuit Breaker y Timeout.
    """
    # 2. Verificar si el fusible nos permite pasar
    fusible_pagos.verificar_disponibilidad()

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_ESTRICTO) as cliente:
            print(f"📡 Intentando conectar con pasarela para pedido {id_pedido}...")
            respuesta = await cliente.post(
                url_api,
                json={"pedido_id": id_pedido, "monto": monto}
            )
            respuesta.raise_for_status()
            
            # Éxito: restablecemos el circuito a CERRADO
            fusible_pagos.registrar_exito()
            return {
                "estado": "aprobado",
                "codigo_autorizacion": "AUTH-778899",
                "mensaje": "Pago procesado exitosamente por el banco."
            }

    except (httpx.TimeoutException, httpx.HTTPStatusError, httpx.RequestError) as error_red:
        # Registramos el fallo para proteger el servidor
        fusible_pagos.registrar_fallo()
        raise error_red

async def servicio_checkout_con_fallback(id_pedido: str, monto: float, url_proveedor: str) -> dict:
    """
    Punto de entrada de la tienda online con PLAN DE CONTINGENCIA (Fallback).
    """
    try:
        # Intentamos el cobro normal
        resultado = await procesar_pago_con_proveedor(url_proveedor, id_pedido, monto)
        return resultado

    except (CircuitoCortadoError, httpx.TimeoutException, httpx.HTTPError) as excepcion:
        # 3. PLAN DE CONTINGENCIA EMPRESARIAL + RESCATE CON IA:
        # No mostramos un error 500 al cliente; la IA rescata la venta con empatía.
        print(f"⚡ [CIRCUIT BREAKER ACTIVADO] Cortando tráfico por: {excepcion}")
        print("🤖 [IA SMART FALLBACK] Activando rescate semántico para no perder la venta...")
        return {
            "estado": "pedido_reservado_offline",
            "pedido_id": id_pedido,
            "monto": monto,
            "mensaje": "La red bancaria externa está congestionada.",
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

# --- Demostración en consola para pruebas ---
async def demo():
    print("=" * 65)
    print("🧘‍♂️ DEMOSTRACIÓN DE RESILIENCIA CON CIRCUIT BREAKER Y HTTPX")
    print("=" * 65)

    # Caso 1: Pasarela caída (simulamos URL con timeout forzado)
    url_caida = "https://httpbin.org/delay/5" # Tarda 5s, pero nuestro timeout es de 2s

    print("\n--- PASO 1: Tres intentos sucesivos fallan por timeout ---")
    for intento in range(1, 4):
        print(f"\n[Intento #{intento}]")
        respuesta = await servicio_checkout_con_fallback(f"PED-00{intento}", 99.0, url_caida)
        print(f"Respuesta al usuario: {respuesta['estado']} ➔ {respuesta['mensaje']}")

    print("\n--- PASO 2: Cuarto intento inmediato (El circuito ya está ABIERTO) ---")
    respuesta_inmediata = await servicio_checkout_con_fallback("PED-004", 120.0, url_caida)
    print(f"Respuesta inmediata sin esperar 2s: {respuesta_inmediata['estado']}")

    print("\n--- PASO 3: Esperamos el tiempo de enfriamiento (4 segundos) ---")
    await asyncio.sleep(4.5)

    print("\n--- PASO 4: Probamos con una pasarela sana en modo SEMIABIERTO ---")
    url_sana = "https://httpbin.org/status/200" # Responde 200 OK inmediatamente
    respuesta_recuperada = await servicio_checkout_con_fallback("PED-005", 85.0, url_sana)
    print(f"Resultado tras recuperación: {respuesta_recuperada['estado']}")
    print(f"Estado final del circuito: {fusible_pagos.estado.value} 🟢 (Todo en orden)")

if __name__ == "__main__":
    asyncio.run(demo())
