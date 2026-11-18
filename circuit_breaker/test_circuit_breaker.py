"""
test_circuit_breaker.py
-----------------------
Suite de QA Automation y Resiliencia.
Valida el correcto funcionamiento de los 3 estados del Circuit Breaker
(CERRADO, ABIERTO, SEMIABIERTO) y la ejecución del Fallback sin requerir red externa.
Compatible con Pytest y con el ejecutor estándar unittest de Python.
"""

import time
import unittest
import asyncio
from unittest.mock import AsyncMock, patch

try:
    import httpx
except ImportError:
    import httpx2 as httpx

try:
    from circuit_breaker.cliente_zen_circuit_breaker import (
        CircuitBreaker,
        EstadoCircuito,
        CircuitoCortadoError,
        servicio_checkout_con_fallback
    )
except ImportError:
    from cliente_zen_circuit_breaker import (
        CircuitBreaker,
        EstadoCircuito,
        CircuitoCortadoError,
        servicio_checkout_con_fallback
    )

class TestCircuitBreaker(unittest.TestCase):

    def setUp(self):
        """Crea una instancia limpia del Circuit Breaker para cada prueba."""
        self.fusible = CircuitBreaker(limite_fallos=3, tiempo_enfriamiento_segundos=1.0)

    def test_circuito_inicia_cerrado(self):
        """Verifica que el circuito comience en estado CERRADO y con 0 fallos."""
        self.assertEqual(self.fusible.estado, EstadoCircuito.CERRADO)
        self.assertEqual(self.fusible.contador_fallos_consecutivos, 0)

    def test_un_fallo_no_abre_el_circuito(self):
        """Un solo fallo registra la incidencia, pero el circuito sigue CERRADO."""
        self.fusible.registrar_fallo()
        self.assertEqual(self.fusible.contador_fallos_consecutivos, 1)
        self.assertEqual(self.fusible.estado, EstadoCircuito.CERRADO)

    def test_limite_de_fallos_abre_el_circuito(self):
        """Tres fallos consecutivos deben cambiar el estado a ABIERTO."""
        self.fusible.registrar_fallo()
        self.fusible.registrar_fallo()
        self.assertEqual(self.fusible.estado, EstadoCircuito.CERRADO)
        
        # Tercer fallo consecutivo
        self.fusible.registrar_fallo()
        self.assertEqual(self.fusible.estado, EstadoCircuito.ABIERTO)
        self.assertEqual(self.fusible.contador_fallos_consecutivos, 3)

    def test_circuito_abierto_bloquea_peticiones_rapido(self):
        """Cuando el circuito está abierto, no se permite ninguna llamada."""
        for _ in range(3):
            self.fusible.registrar_fallo()
        
        self.assertEqual(self.fusible.estado, EstadoCircuito.ABIERTO)
        with self.assertRaises(CircuitoCortadoError):
            self.fusible.verificar_disponibilidad()

    def test_tiempo_enfriamiento_permite_modo_semiabierto(self):
        """Tras el tiempo de espera, el circuito pasa de ABIERTO a SEMIABIERTO."""
        for _ in range(3):
            self.fusible.registrar_fallo()
        
        self.assertEqual(self.fusible.estado, EstadoCircuito.ABIERTO)
        
        # Simulamos el paso del tiempo de enfriamiento (1.1 segundos)
        time.sleep(1.1)
        
        # Al verificar disponibilidad, no debe lanzar error sino pasar a SEMIABIERTO
        self.fusible.verificar_disponibilidad()
        self.assertEqual(self.fusible.estado, EstadoCircuito.SEMIABIERTO)

    def test_exito_en_semiabierto_restaura_circuito_cerrado(self):
        """Una llamada exitosa cierra el circuito y reinicia el contador de fallos."""
        self.fusible.estado = EstadoCircuito.SEMIABIERTO
        self.fusible.contador_fallos_consecutivos = 3
        
        self.fusible.registrar_exito()
        self.assertEqual(self.fusible.estado, EstadoCircuito.CERRADO)
        self.assertEqual(self.fusible.contador_fallos_consecutivos, 0)

    def test_fallback_empresarial_se_activa_ante_timeout(self):
        """
        Simula una excepción de timeout y valida que la función de checkout
        no colapse, sino que devuelva el plan de contingencia offline.
        """
        with patch.object(httpx.AsyncClient, "post", side_effect=httpx.TimeoutException("Servidor no responde")):
            resultado = asyncio.run(
                servicio_checkout_con_fallback(
                    id_pedido="PED-TEST-001",
                    monto=50.0,
                    url_proveedor="https://api-falsa-de-prueba.com/cobrar"
                )
            )
            
            # Validaciones de negocio
            self.assertEqual(resultado["estado"], "pedido_reservado_offline")
            self.assertEqual(resultado["pedido_id"], "PED-TEST-001")
            self.assertIn("Transferencia Bancaria", resultado["alternativa_sugerida"])
            self.assertEqual(resultado["tiempo_reserva_minutos"], 120)

if __name__ == "__main__":
    unittest.main()
