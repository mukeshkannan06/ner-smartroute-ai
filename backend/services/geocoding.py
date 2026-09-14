"""
India-Wide Geocoding Service — Nominatim (OpenStreetMap) + Comprehensive Knowledge Base
---------------------------------------------------------------------------------------
Converts any location name in India to lat/lon coordinates with elevation & terrain tags.
Supports instant cached lookup for 50+ major logistics hubs/cities across all regions.
"""
import os
import time
import asyncio
from typing import Optional, Dict, List, Any
from dataclasses import dataclass

import httpx

NOMINATIM_BASE_URL = os.getenv("NOMINATIM_BASE_URL", "https://nominatim.openstreetmap.org")
NOMINATIM_TIMEOUT = float(os.getenv("NOMINATIM_TIMEOUT", "8"))

_last_request_time: float = 0.0
_geocoding_cache: Dict[str, List["GeocodingResult"]] = {}


@dataclass
class GeocodingResult:
    name: str
    display_name: str
    lat: float
    lon: float
    type: str
    state: str = "India"
    terrain: str = "plain"  # plain, hilly, coastal, plateau
    elevation_m: float = 50.0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "lat": self.lat,
            "lon": self.lon,
            "type": self.type,
            "state": self.state,
            "terrain": self.terrain,
            "elevation_m": self.elevation_m,
        }


# Comprehensive Pan-India Known Locations (Instant zero-latency lookup)
KNOWN_LOCATIONS: Dict[str, GeocodingResult] = {
    # South India
    "chennai": GeocodingResult("Chennai", "Chennai, Tamil Nadu, India", 13.0827, 80.2707, "city", "Tamil Nadu", "coastal", 6.0),
    "bengaluru": GeocodingResult("Bengaluru", "Bengaluru, Karnataka, India", 12.9716, 77.5946, "city", "Karnataka", "plateau", 920.0),
    "bangalore": GeocodingResult("Bengaluru", "Bengaluru, Karnataka, India", 12.9716, 77.5946, "city", "Karnataka", "plateau", 920.0),
    "hyderabad": GeocodingResult("Hyderabad", "Hyderabad, Telangana, India", 17.3850, 78.4867, "city", "Telangana", "plateau", 542.0),
    "kochi": GeocodingResult("Kochi", "Kochi, Ernakulam, Kerala, India", 9.9312, 76.2673, "city", "Kerala", "coastal", 3.0),
    "coimbatore": GeocodingResult("Coimbatore", "Coimbatore, Tamil Nadu, India", 11.0168, 76.9558, "city", "Tamil Nadu", "plain", 411.0),
    "madurai": GeocodingResult("Madurai", "Madurai, Tamil Nadu, India", 9.9252, 78.1198, "city", "Tamil Nadu", "plain", 101.0),
    "visakhapatnam": GeocodingResult("Visakhapatnam", "Visakhapatnam, Andhra Pradesh, India", 17.6868, 83.2185, "city", "Andhra Pradesh", "coastal", 45.0),
    "vijayawada": GeocodingResult("Vijayawada", "Vijayawada, Andhra Pradesh, India", 16.5062, 80.6480, "city", "Andhra Pradesh", "plain", 11.0),
    "thiruvananthapuram": GeocodingResult("Thiruvananthapuram", "Thiruvananthapuram, Kerala, India", 8.5241, 76.9366, "city", "Kerala", "coastal", 10.0),
    "mangalore": GeocodingResult("Mangalore", "Mangalore, Dakshina Kannada, Karnataka, India", 12.9141, 74.8560, "city", "Karnataka", "coastal", 22.0),

    # West India
    "mumbai": GeocodingResult("Mumbai", "Mumbai, Maharashtra, India", 19.0760, 72.8777, "city", "Maharashtra", "coastal", 14.0),
    "pune": GeocodingResult("Pune", "Pune, Maharashtra, India", 18.5204, 73.8567, "city", "Maharashtra", "plateau", 560.0),
    "ahmedabad": GeocodingResult("Ahmedabad", "Ahmedabad, Gujarat, India", 23.0225, 72.5714, "city", "Gujarat", "plain", 53.0),
    "surat": GeocodingResult("Surat", "Surat, Gujarat, India", 21.1702, 72.8311, "city", "Gujarat", "coastal", 13.0),
    "nagpur": GeocodingResult("Nagpur", "Nagpur, Maharashtra, India", 21.1458, 79.0882, "city", "Maharashtra", "plain", 310.0),
    "goa": GeocodingResult("Panaji", "Panaji, Goa, India", 15.4909, 73.8278, "city", "Goa", "coastal", 7.0),
    "panaji": GeocodingResult("Panaji", "Panaji, Goa, India", 15.4909, 73.8278, "city", "Goa", "coastal", 7.0),
    "nashik": GeocodingResult("Nashik", "Nashik, Maharashtra, India", 19.9975, 73.7898, "city", "Maharashtra", "plateau", 600.0),

    # North India
    "delhi": GeocodingResult("Delhi", "New Delhi, Delhi, India", 28.6139, 77.2090, "city", "Delhi", "plain", 216.0),
    "new delhi": GeocodingResult("New Delhi", "New Delhi, Delhi, India", 28.6139, 77.2090, "city", "Delhi", "plain", 216.0),
    "jaipur": GeocodingResult("Jaipur", "Jaipur, Rajasthan, India", 26.9124, 75.7873, "city", "Rajasthan", "plain", 431.0),
    "lucknow": GeocodingResult("Lucknow", "Lucknow, Uttar Pradesh, India", 26.8467, 80.9462, "city", "Uttar Pradesh", "plain", 123.0),
    "kanpur": GeocodingResult("Kanpur", "Kanpur, Uttar Pradesh, India", 26.4499, 80.3319, "city", "Uttar Pradesh", "plain", 126.0),
    "chandigarh": GeocodingResult("Chandigarh", "Chandigarh, India", 30.7333, 76.7794, "city", "Chandigarh", "plain", 321.0),
    "dehradun": GeocodingResult("Dehradun", "Dehradun, Uttarakhand, India", 30.3165, 78.0322, "city", "Uttarakhand", "hilly", 640.0),
    "rishikesh": GeocodingResult("Rishikesh", "Rishikesh, Dehradun, Uttarakhand, India", 30.0869, 78.2676, "city", "Uttarakhand", "hilly", 372.0),
    "shimla": GeocodingResult("Shimla", "Shimla, Himachal Pradesh, India", 31.1048, 77.1734, "city", "Himachal Pradesh", "hilly", 2276.0),
    "srinagar": GeocodingResult("Srinagar", "Srinagar, Jammu and Kashmir, India", 34.0837, 74.7973, "city", "Jammu and Kashmir", "hilly", 1585.0),
    "jammu": GeocodingResult("Jammu", "Jammu, Jammu and Kashmir, India", 32.7266, 74.8570, "city", "Jammu and Kashmir", "hilly", 327.0),
    "varanasi": GeocodingResult("Varanasi", "Varanasi, Uttar Pradesh, India", 25.3176, 82.9739, "city", "Uttar Pradesh", "plain", 80.0),
    "agra": GeocodingResult("Agra", "Agra, Uttar Pradesh, India", 27.1767, 78.0081, "city", "Uttar Pradesh", "plain", 171.0),

    # East India
    "kolkata": GeocodingResult("Kolkata", "Kolkata, West Bengal, India", 22.5726, 88.3639, "city", "West Bengal", "coastal", 9.0),
    "bhubaneswar": GeocodingResult("Bhubaneswar", "Bhubaneswar, Khordha, Odisha, India", 20.2961, 85.8245, "city", "Odisha", "coastal", 45.0),
    "cuttack": GeocodingResult("Cuttack", "Cuttack, Odisha, India", 20.4625, 85.8830, "city", "Odisha", "plain", 36.0),
    "balasore": GeocodingResult("Balasore", "Balasore, Odisha, India", 21.4934, 86.9135, "city", "Odisha", "coastal", 16.0),
    "patna": GeocodingResult("Patna", "Patna, Bihar, India", 25.5941, 85.1376, "city", "Bihar", "plain", 53.0),
    "ranchi": GeocodingResult("Ranchi", "Ranchi, Jharkhand, India", 23.3441, 85.3096, "city", "Jharkhand", "plateau", 651.0),
    "jamshedpur": GeocodingResult("Jamshedpur", "Jamshedpur, Jharkhand, India", 22.8046, 86.2029, "city", "Jharkhand", "plain", 135.0),
    "siliguri": GeocodingResult("Siliguri", "Siliguri, Darjeeling, West Bengal, India", 26.7271, 88.3953, "city", "West Bengal", "plain", 122.0),

    # North-East India
    "guwahati": GeocodingResult("Guwahati", "Guwahati, Kamrup Metropolitan, Assam, India", 26.1445, 91.7362, "city", "Assam", "plain", 55.0),
    "shillong": GeocodingResult("Shillong", "Shillong, East Khasi Hills, Meghalaya, India", 25.5788, 91.8933, "city", "Meghalaya", "hilly", 1525.0),
    "silchar": GeocodingResult("Silchar", "Silchar, Cachar, Assam, India", 24.8333, 92.7789, "city", "Assam", "plain", 25.0),
    "dimapur": GeocodingResult("Dimapur", "Dimapur, Nagaland, India", 25.9091, 93.7267, "city", "Nagaland", "plain", 145.0),
    "kohima": GeocodingResult("Kohima", "Kohima, Nagaland, India", 25.6751, 94.1086, "city", "Nagaland", "hilly", 1444.0),
    "imphal": GeocodingResult("Imphal", "Imphal, Manipur, India", 24.8170, 93.9368, "city", "Manipur", "hilly", 786.0),
    "jorhat": GeocodingResult("Jorhat", "Jorhat, Assam, India", 26.7509, 94.2037, "city", "Assam", "plain", 116.0),
    "aizawl": GeocodingResult("Aizawl", "Aizawl, Mizoram, India", 23.7271, 92.7176, "city", "Mizoram", "hilly", 1132.0),
    "tezpur": GeocodingResult("Tezpur", "Tezpur, Sonitpur, Assam, India", 26.6338, 92.7837, "city", "Assam", "plain", 48.0),
    "nagaon": GeocodingResult("Nagaon", "Nagaon, Assam, India", 26.3506, 92.6840, "city", "Assam", "plain", 60.0),
    "agartala": GeocodingResult("Agartala", "Agartala, West Tripura, Tripura, India", 23.8315, 91.2868, "city", "Tripura", "plain", 15.0),
    "gangtok": GeocodingResult("Gangtok", "Gangtok, East Sikkim, Sikkim, India", 27.3389, 88.6065, "city", "Sikkim", "hilly", 1650.0),
    "itanagar": GeocodingResult("Itanagar", "Itanagar, Papum Pare, Arunachal Pradesh, India", 27.0844, 93.6053, "city", "Arunachal Pradesh", "hilly", 750.0),
}


async def _rate_limit():
    """Enforce 1 request per second for Nominatim."""
    global _last_request_time
    now = time.time()
    elapsed = now - _last_request_time
    if elapsed < 1.0:
        await asyncio.sleep(1.0 - elapsed)
    _last_request_time = time.time()


async def geocode(query: str) -> Optional[List[GeocodingResult]]:
    """
    Geocode any location name in India to coordinates.
    Checks cached/known locations first, then queries Nominatim.
    """
    query_lower = query.strip().lower()
    if not query_lower:
        return None

    # Check cache first
    if query_lower in _geocoding_cache:
        return _geocoding_cache[query_lower]

    if query_lower in KNOWN_LOCATIONS:
        res = [KNOWN_LOCATIONS[query_lower]]
        _geocoding_cache[query_lower] = res
        return res

    # Check partial match on known locations
    for k, v in KNOWN_LOCATIONS.items():
        if k in query_lower or query_lower in k:
            res = [v]
            _geocoding_cache[query_lower] = res
            return res

    # Query Nominatim API with India bounding box bias
    try:
        await _rate_limit()
        headers = {"User-Agent": "IndiaSmartRouteAI/1.0 (disaster-aware routing platform)"}
        params = {
            "q": query,
            "format": "json",
            "countrycodes": "in",
            "limit": 5,
            "addressdetails": 1,
        }

        async with httpx.AsyncClient(timeout=NOMINATIM_TIMEOUT) as client:
            response = await client.get(
                f"{NOMINATIM_BASE_URL}/search",
                params=params,
                headers=headers,
            )
            if response.status_code == 200:
                data = response.json()
                if data:
                    results = []
                    for item in data:
                        display = item.get("display_name", "")
                        state = item.get("address", {}).get("state", "India")
                        lat = float(item["lat"])
                        lon = float(item["lon"])
                        
                        # Infer terrain
                        terrain = "hilly" if lat > 27.0 or (lat > 8.0 and lat < 21.0 and lon < 76.0) else "plain"
                        res = GeocodingResult(
                            name=item.get("name") or query.capitalize(),
                            display_name=display,
                            lat=lat,
                            lon=lon,
                            type=item.get("type", "location"),
                            state=state,
                            terrain=terrain,
                        )
                        results.append(res)
                    _geocoding_cache[query_lower] = results
                    return results
    except Exception as e:
        print(f"Geocoding fallback exception for '{query}': {e}")

    # Fallback to closest known location or center
    default_res = [GeocodingResult(query.capitalize(), f"{query.capitalize()}, India", 20.5937, 78.9629, "city")]
    _geocoding_cache[query_lower] = default_res
    return default_res
