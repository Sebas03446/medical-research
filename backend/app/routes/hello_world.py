from fastapi import APIRouter, HTTPException
from app.services.medical_api import get_access_token, get_specialisations
from app.config import settings
import requests


router = APIRouter()

@router.get("/")
async def hello_world():
    return {"response": "Hello, I am here!"}


@router.get("/token")
async def token():
    """
    Retrieve the access token using credentials from the environment.
    """
    try:
        token_data = get_access_token(settings.API_KEY_MEDICAL_API, settings.SECRET_KEY_MEDICAL_API)
        return token_data
    except requests.exceptions.HTTPError as http_err:
        # Return a 400 error if the token request fails (e.g., wrong credentials)
        raise HTTPException(status_code=400, detail=f"HTTP error: {http_err}")
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"An error occurred: {err}")

@router.get("/mock/specialisations")
async def mock_specialisations():
    """
    A mock endpoint to simulate the response for specialisations using fixed input:
      - Symptom ID: 981
      - Gender: "male"
      - Age: 20 (converted to year_of_birth, assuming current year is 2025 → 2005)
    
    Returns a mocked list of specialisations.
    """
    # Fixed input values
    token = get_access_token(settings.API_KEY_MEDICAL_API, settings.SECRET_KEY_MEDICAL_API)["Token"]
    symptoms = [981]
    gender = "male"
    # Convert age 20 to year_of_birth (assuming current year 2025 for example)
    year_of_birth = 2025 - 20  # i.e., 2005
    try: 
        data = get_specialisations(token,symptoms , gender, year_of_birth)
        return data
    except requests.exceptions.HTTPError as http_err:
        raise HTTPException(status_code=400, detail=f"HTTP error: {http_err}")
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"An error occurred: {err}")
    
    
    