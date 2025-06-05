
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI()

GOOGLE_SOLAR_API_KEY = "YOUR_GOOGLE_SOLAR_API_KEY"
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
    except KeyError:
        raise HTTPException(status_code=400, detail="Incomplete solar data")

    system_size_kw = (panel_count * PANEL_WATTAGE) / 1000
    estimated_cost = system_size_kw * COST_PER_WATT * 1000
    estimated_savings = annual_kwh * 0.20  # assume 20 cents/kWh utility rate

    return SolarQuoteResponse(
        annual_kwh=annual_kwh,
        panel_count=panel_count,
        system_size_kw=system_size_kw,
        estimated_cost=estimated_cost,
        estimated_savings=estimated_savings,
        lat=lat,
        lng=lng
    )
