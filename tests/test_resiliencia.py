def test_escudo_global_atrapa_error_500_con_trace_id(client):
    """
    Verifica que ante un fallo no previsto (ej. 1/0), el manejador global
    devuelva un 500 controlado con 'error_id' sin tumbar el proceso del servidor.
    """
    response = client.get("/api/v1/pedidos/simular/error-inesperado")
    assert response.status_code == 500
    data = response.json()
    assert data["status"] == "error"
    assert "error_id" in data
    assert len(data["error_id"]) == 8
    assert "soporte" in data

def test_servidor_sigue_vivo_despues_de_un_error_500(client):
    """
    Verifica la resiliencia zen: después de un error 500, el servidor
    continúa respondiendo con total normalidad a las demás peticiones.
    """
    # 1. Provocamos el fallo
    client.get("/api/v1/pedidos/simular/error-inesperado")

    # 2. El servidor debe seguir respondiendo en paz
    health_response = client.get("/api/v1/health")
    assert health_response.status_code == 200
    assert health_response.json()["status"] == "healthy"

def test_checkout_resiliente_fallback_ante_pasarela_caida(client):
    """
    Verifica que ante una pasarela caída (timeout), el endpoint devuelva
    el Fallback semántico VIP con código QR en lugar de un error 503.
    """
    from unittest.mock import patch
    import httpx

    # Creamos un pedido previo
    crear = client.post(
        "/api/v1/pedidos/",
        json={"cliente": "Capyzen Tester", "plato": "Ramen Zen", "monto": 45.0, "cupones": 1}
    )
    pedido_id = crear.json()["id"]

    # Simulamos caída externa
    with patch.object(httpx.AsyncClient, "post", side_effect=httpx.TimeoutException("Timeout pasarela")):
        resp = client.post(f"/api/v1/pedidos/{pedido_id}/checkout-resiliente")
        assert resp.status_code == 200
        data = resp.json()
        assert data["estado"] == "pedido_reservado_offline"
        assert data["rescate_ia"]["activo"] is True
        assert "qr-transferencia" in data["rescate_ia"]["enlace_qr"]

