from datetime import date, timedelta
import random
from typing import List, Optional


class MockIntegrationClient:
    """
    Mock client for Integration Service.
    Returns realistic mock data for weather and POI (Points of Interest).
    Will be replaced with real HTTP client when Integration Service is ready.
    """
    
    # Ukrainian cities with coordinates
    CITY_DATA = {
        "київ": {"lat": 50.4501, "lng": 30.5234, "name_en": "Kyiv"},
        "львів": {"lat": 49.8397, "lng": 24.0297, "name_en": "Lviv"},
        "одеса": {"lat": 46.4825, "lng": 30.7233, "name_en": "Odesa"},
        "харків": {"lat": 49.9935, "lng": 36.2304, "name_en": "Kharkiv"},
        "дніпро": {"lat": 48.4647, "lng": 35.0462, "name_en": "Dnipro"},
    }
    
    # POI data by category
    POI_DATABASE = {
        "київ": {
            "history": [
                {"name": "Софійський собор", "lat": 50.4529, "lng": 30.5143, "rating": 4.9, "price_uah": 150},
                {"name": "Києво-Печерська лавра", "lat": 50.4346, "lng": 30.5580, "rating": 4.8, "price_uah": 100},
                {"name": "Золоті ворота", "lat": 50.4489, "lng": 30.5133, "rating": 4.7, "price_uah": 80},
            ],
            "food": [
                {"name": "Пузата Хата", "lat": 50.4501, "lng": 30.5234, "rating": 4.5, "price_uah": 200},
                {"name": "Канапа", "lat": 50.4532, "lng": 30.5189, "rating": 4.8, "price_uah": 800},
                {"name": "Остання Барикада", "lat": 50.4478, "lng": 30.5223, "rating": 4.6, "price_uah": 500},
            ],
            "culture": [
                {"name": "Національний художній музей", "lat": 50.4445, "lng": 30.5283, "rating": 4.7, "price_uah": 100},
                {"name": "Пінчук Арт Центр", "lat": 50.4403, "lng": 30.5205, "rating": 4.6, "price_uah": 0},
            ],
            "nature": [
                {"name": "Маріїнський парк", "lat": 50.4462, "lng": 30.5388, "rating": 4.7, "price_uah": 0},
                {"name": "Гідропарк", "lat": 50.4524, "lng": 30.5766, "rating": 4.4, "price_uah": 0},
            ],
        },
        "львів": {
            "history": [
                {"name": "Площа Ринок", "lat": 49.8419, "lng": 24.0316, "rating": 4.9, "price_uah": 0},
                {"name": "Високий замок", "lat": 49.8485, "lng": 24.0396, "rating": 4.7, "price_uah": 0},
                {"name": "Личаківський цвинтар", "lat": 49.8352, "lng": 24.0564, "rating": 4.8, "price_uah": 50},
            ],
            "food": [
                {"name": "Львівська Копальня Кави", "lat": 49.8419, "lng": 24.0316, "rating": 4.7, "price_uah": 300},
                {"name": "Криївка", "lat": 49.8411, "lng": 24.0323, "rating": 4.6, "price_uah": 400},
                {"name": "Бачевських", "lat": 49.8389, "lng": 24.0286, "rating": 4.8, "price_uah": 600},
            ],
            "culture": [
                {"name": "Львівська опера", "lat": 49.8440, "lng": 24.0261, "rating": 4.9, "price_uah": 300},
                {"name": "Палац Потоцьких", "lat": 49.8419, "lng": 24.0316, "rating": 4.6, "price_uah": 80},
            ],
            "nature": [
                {"name": "Стрийський парк", "lat": 49.8279, "lng": 24.0238, "rating": 4.8, "price_uah": 0},
            ],
        },
    }
    
    WEATHER_CONDITIONS = ["sunny", "partly_cloudy", "cloudy", "rainy", "clear"]
    
    async def get_weather(
        self, 
        city: str, 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None
    ) -> dict:
        """Return mock weather forecast for a city."""
        city_key = city.lower().strip()
        city_info = self.CITY_DATA.get(city_key, {"lat": 50.0, "lng": 30.0, "name_en": city})
        
        if not start_date:
            start_date = date.today()
        if not end_date:
            end_date = start_date + timedelta(days=3)
        
        forecast = []
        current_date = start_date
        while current_date <= end_date:
            forecast.append({
                "date": str(current_date),
                "temp_min_c": random.randint(10, 18),
                "temp_max_c": random.randint(18, 28),
                "condition": random.choice(self.WEATHER_CONDITIONS),
                "humidity_percent": random.randint(40, 80),
                "precipitation_chance": random.randint(0, 40),
            })
            current_date += timedelta(days=1)
        
        return {
            "city": city,
            "city_en": city_info["name_en"],
            "coordinates": {"lat": city_info["lat"], "lng": city_info["lng"]},
            "forecast": forecast,
        }
    
    async def search_pois(
        self, 
        city: str, 
        interests: List[str]
    ) -> List[dict]:
        """Return mock POI data based on city and interests."""
        city_key = city.lower().strip()
        city_pois = self.POI_DATABASE.get(city_key, {})
        
        result = []
        for interest in interests:
            interest_key = interest.lower().strip()
            pois = city_pois.get(interest_key, [])
            for poi in pois:
                result.append({
                    **poi,
                    "category": interest_key,
                    "city": city,
                })
        
        # Add default POI if nothing found
        if not result:
            city_info = self.CITY_DATA.get(city_key, {"lat": 50.0, "lng": 30.0})
            result.append({
                "name": f"Центр міста {city}",
                "lat": city_info["lat"],
                "lng": city_info["lng"],
                "rating": 4.5,
                "price_uah": 0,
                "category": "general",
                "city": city,
            })
        
        return result
    
    async def get_city_info(self, city: str) -> dict:
        """Get basic city information."""
        city_key = city.lower().strip()
        city_info = self.CITY_DATA.get(city_key)
        
        if city_info:
            return {
                "name": city.title(),
                "name_en": city_info["name_en"],
                "coordinates": {"lat": city_info["lat"], "lng": city_info["lng"]},
                "country": "Україна",
                "timezone": "Europe/Kyiv",
            }
        
        return {
            "name": city.title(),
            "name_en": city.title(),
            "coordinates": {"lat": 50.0, "lng": 30.0},
            "country": "Україна",
            "timezone": "Europe/Kyiv",
        }
