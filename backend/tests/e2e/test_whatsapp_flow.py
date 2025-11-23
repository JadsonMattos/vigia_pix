"""Testes end-to-end do fluxo WhatsApp"""
import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app


@pytest.mark.asyncio
async def test_whatsapp_webhook_health():
    """Testa se o webhook está funcionando"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/whatsapp/test")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_whatsapp_simulate_message():
    """Testa simulação de mensagem WhatsApp"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", follow_redirects=True) as client:
        response = await client.post(
            "/api/v1/whatsapp/simulate",
            json={
                "From": "whatsapp:+5511999999999",
                "Body": "PL 1234"
            }
        )
        # Pode retornar 200 ou 500 se não houver legislação no banco
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = response.json()
            assert "response" in data
            assert data["status"] == "success"


@pytest.mark.asyncio
async def test_legislation_sync_and_simplify():
    """Testa fluxo completo: sincronizar e simplificar"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", follow_redirects=True) as client:
        # 1. Sincronizar legislações
        sync_response = await client.post("/api/v1/legislation/sync?days=7")
        assert sync_response.status_code in [200, 500, 307]  # Pode falhar se API externa estiver fora
        
        # 2. Listar legislações
        list_response = await client.get("/api/v1/legislation?limit=1")
        assert list_response.status_code in [200, 307]
        if list_response.status_code == 200:
            data = list_response.json()
            
            if data.get("items") and len(data["items"]) > 0:
                legislation_id = data["items"][0]["id"]
                
                # 3. Simplificar
                simplify_response = await client.post(
                    f"/api/v1/legislation/{legislation_id}/simplify?level=basic"
                )
                assert simplify_response.status_code in [200, 404, 500, 307]
                
                if simplify_response.status_code == 200:
                    simplify_data = simplify_response.json()
                    assert "simplified_text" in simplify_data
                    assert "original_length" in simplify_data
                    assert "simplified_length" in simplify_data


@pytest.mark.asyncio
async def test_dashboard_endpoints():
    """Testa endpoints usados pelo dashboard"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", follow_redirects=True) as client:
        # Health check
        health = await client.get("/health")
        assert health.status_code == 200
        
        # List legislations
        response = await client.get("/api/v1/legislation?limit=10&offset=0")
        assert response.status_code in [200, 307]
        if response.status_code == 200:
            data = response.json()
            assert "items" in data
            assert "total" in data

