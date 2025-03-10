import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check_endpoint(client: AsyncClient):
    """Test that the health check endpoint returns 200 OK with expected data."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"} 