from datetime import date
from typing import List, Optional
import httpx

from app.core.config import settings


class IntegrationClient:
    """
    HTTP client for Integration Service.
    Replaces MockIntegrationClient with real API calls.
    """
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or settings.INTEGRATION_SERVICE_URL
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_weather(
        self, 
        city: str, 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None
    ) -> dict:
        """Get weather forecast for a city."""
        params = {"city": city}
        if start_date:
            params["start_date"] = str(start_date)
        if end_date:
            params["end_date"] = str(end_date)
        
        response = await self.client.get(
            f"{self.base_url}/weather/city",
            params=params,
        )
        response.raise_for_status()
        return response.json()["data"]
    
    async def search_pois(
        self, 
        city: str, 
        interests: List[str]
    ) -> List[dict]:
        """Search POIs by city and interests."""
        response = await self.client.post(
            f"{self.base_url}/maps/pois",
            json={"city": city, "interests": interests}
        )
        response.raise_for_status()
        return response.json()["data"]
    
    async def get_city_info(self, city: str) -> dict:
        """Get city information."""
        response = await self.client.get(
            f"{self.base_url}/maps/city",
            params={"city": city}
        )
        response.raise_for_status()
        return response.json()["data"]
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
