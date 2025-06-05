from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

# Initialize FastAPI
app = FastAPI()

# ✅ CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for development)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Pydantic model for incoming request
class SolarRequest(BaseModel):
    address: str
    monthly_usage_kwh: float

# ✅ Solar Quote API endpoint
@app.post("/get_solar_quote")
async def get_solar_quote(request: SolarRequest):
    # Your actual Google Solar API Key
    GOOGLE_API_KEY = "AIzaSyCnv-5y1zC-F-dDvjtL--yiCzkJO74sF_U"

    GOOGLE_API_URL = "https://solar.googleapis.com/v1/buildingInsights:findClosest"

    params = {
        "key": GOOGLE_API_KEY,
        "location": request.address,
        "requiredQuality": "HIGH"
    }

    response = requests.get(GOOGLE_API_URL, params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch solar data from Google API")

    data = response.json()

    try:
        solar_potential = data['solarPotential']
        annual_kwh = solar_potential['maxArrayProductionKwYear']
        panel_count = solar_potential['maxArrayPanelsCount']
        lat = solar_potential['center']['latitude']
        lng = solar_potential['center']['longitude']
        roof_segments = solar_potential.get('roofSegmentStats', [])
    except KeyError:
        raise HTTPException(status_code=400, detail="Incomplete solar data from Google API")

    estimated_cost = (panel_count * 400) / 1000 * 3.00 * 1000  # Assuming $3.00/Watt
    estimated_savings = annual_kwh * 0.20  # Assuming $0.20 per kWh savings

    return {
        "annual_kwh": annual_kwh,
        "panel_count": panel_count,
        "system_size_kw": (panel_count * 400) / 1000,
        "estimated_cost": estimated_cost,
        "estimated_savings": estimated_savings,
        "lat": lat,
        "lng": lng,
        "roof_segments": roof_segments
    }
