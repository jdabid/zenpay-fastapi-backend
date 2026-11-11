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
