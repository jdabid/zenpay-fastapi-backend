"""
cliente_inseguro.py
-------------------
Demostración del ANTIPATRÓN común en backend:
Hacer peticiones a servicios de terceros sin timeout ni protección de circuito.

Si el banco externo sufre una caída de red o saturación,
esta función se queda congelada indefinidamente, agotando los hilos de CPU
del servidor y provocando un colapso total (Error 504).
"""

import asyncio

try:
    import httpx
except ImportError:
    import httpx2 as httpx

async def cobrar_con_banco_inseguro(id_pedido: str, total_a_pagar: float) -> dict:
    # ❌ ERROR GRAVE: No especificar timeout.
    # Por defecto, la conexión puede quedarse esperando minutos u horas.
    async with httpx.AsyncClient() as cliente:
        print(f"⏳ [INSEGURO] Intentando cobrar pedido {id_pedido} por ${total_a_pagar}...")
        
        # Si esta URL externa no responde, el servidor entero se congela
        respuesta = await cliente.post(
            "https://httpbin.org/delay/10", # Simula un proveedor que tarda 10 segundos
            json={"pedido": id_pedido, "total": total_a_pagar}
        )
        return respuesta.json()

async def main():
    print("🚨 Ejecutando cliente inseguro sin límites de tiempo...")
    try:
        resultado = await cobrar_con_banco_inseguro("PED-9901", 150.0)
        print("Respuesta recibida:", resultado)
    except Exception as error:
        print("💥 Error no controlado en el servidor:", error)

if __name__ == "__main__":
    asyncio.run(main())
