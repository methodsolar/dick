from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI()

# ✅ YOUR GOOGLE SOLAR API KEY here
GOOGLE_SOLAR_API_KEY = "AIzaSyCnv-5y1zC-F-dDvjtL--yiCzkJO74sF_U"
GOOGLE_SOLAR_API_URL = "https://solar.googleapis.com/v1/buildingInsights:findClosest"

class SolarRequest(BaseModel):
    address: str
    monthly_usage_kwh: float

class SolarQuoteResponse(BaseModel):
    annual_kwh: float
    panel_count: int
    system_size_kw: float
    estimated_cost: float
    estimated_savings: float
    lat: float
    lng: float
    roof_segments: list

PANEL_WATTAGE = 400  # watts
COST_PER_WATT = 3.00  # dollars

@app.post("/get_solar_quote", response_model=SolarQuoteResponse)
async def get_solar_quote(request: SolarRequest):
    params = {
        "key": GOOGLE_SOLAR_API_KEY,
        "location": request.address,
        "requiredQuality": "HIGH"
    }

    response = requests.get(GOOGLE_SOLAR_API_URL, params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch solar data")

    data = response.json()

    try:
        solar_potential = data['solarPotential']
        annual_kwh = solar_potential['maxArrayProductionKwYear']
        panel_count = solar_potential['maxArrayPanelsCount']
        lat = solar_potential['center']['latitude']
        lng = solar_potential['center']['longitude']
        roof_segments = solar_potential.get('roofSegmentStats', [])
    except KeyError:
        raise HTTPException(status_code=400, detail="Incomplete solar data")

    return {
        "annual_kwh": annual_kwh,
        "panel_count": panel_count,
        "system_size_kw": (panel_count * PANEL_WATTAGE) / 1000,
        "estimated_cost": (panel_count * PANEL_WATTAGE) / 1000 * COST_PER_WATT * 1000,
        "estimated_savings": annual_kwh * 0.20,
        "lat": lat,
        "lng": lng,
        "roof_segments": roof_segments  # ✅ Added roof segments for frontend map
    }
