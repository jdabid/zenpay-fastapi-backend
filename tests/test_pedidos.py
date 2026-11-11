def test_root_endpoint(client):
    """Verifica que el root responda 200 con mensaje de bienvenida."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_health_check_endpoint(client):
    """Verifica el health check del dojo."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_crear_pedido_valido_status_201(client):
    """Verifica el registro exitoso de un pedido con HTTP 201 Created."""
    payload = {
        "cliente": "Capyzen Senior",
        "plato": "Ramen Zen Tradicional",
        "monto": 45.0,
        "cupones": 3
    }
    response = client.post("/api/v1/pedidos/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["cliente"] == "Capyzen Senior"
    assert data["monto"] == 45.0
    assert data["id"] is not None
    assert data["estado"] == "PAGADO"

def test_crear_pedido_monto_negativo_falla_422(client):
    """Verifica que Pydantic v2 rechace montos <= 0 con HTTP 422."""
    payload = {
        "cliente": "Capyzen",
        "plato": "Té Verde",
        "monto": -10.0,
        "cupones": 1
    }
    response = client.post("/api/v1/pedidos/", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["status"] == "error"

def test_obtener_pedido_existente_status_200(client):
    """Verifica la consulta de un pedido creado previamente."""
    nuevo = client.post("/api/v1/pedidos/", json={
        "cliente": "Junior Dev",
        "plato": "Matcha Latte",
        "monto": 15.0,
        "cupones": 1
    }).json()

    response = client.get(f"/api/v1/pedidos/{nuevo['id']}")
    assert response.status_code == 200
    assert response.json()["cliente"] == "Junior Dev"

def test_obtener_pedido_inexistente_retorna_404(client):
    """Verifica que IDs inexistentes retornen 404 semántico."""
    response = client.get("/api/v1/pedidos/9999")
    assert response.status_code == 404
    assert "no existe" in response.json()["mensaje"]

def test_descuento_promedio_con_cupones_status_200(client):
    """Verifica el cálculo correcto de promedio."""
    nuevo = client.post("/api/v1/pedidos/", json={
        "cliente": "Sensei",
        "plato": "Banquete Zen",
        "monto": 100.0,
        "cupones": 4
    }).json()

    response = client.get(f"/api/v1/pedidos/{nuevo['id']}/descuento-promedio")
    assert response.status_code == 200
    data = response.json()
    assert data["descuento_promedio"] == 25.0

def test_descuento_promedio_cero_cupones_retorna_400(client):
    """Verifica que cero cupones devuelva 400 Bad Request en lugar de colapsar con ZeroDivisionError."""
    nuevo = client.post("/api/v1/pedidos/", json={
        "cliente": "Capyzen",
        "plato": "Sushi Maki",
        "monto": 30.0,
        "cupones": 0
    }).json()

    response = client.get(f"/api/v1/pedidos/{nuevo['id']}/descuento-promedio")
    assert response.status_code == 400
    assert "no tiene cupones aplicados" in response.json()["mensaje"]
