import requests
import hmac
import hashlib
import base64
import json
import os
import app.config as settings


def get_access_token(api_key: str, secret_key: str, response_format: str = "json") -> dict:
    """
    Fetch the access token from the authorization service using HMACMD5 authentication.
    
    :param api_key: The unique client id (username) to access the API.
    :param secret_key: The client password (secret key) used for hashing.
    :param response_format: The format for the returned data (json or xml). Default is "json".
    :return: A dictionary with the token information.
    """
    # Build the URL with the optional format parameter
    uri = f"https://authservice.priaid.ch/login?format={response_format}"
    
    # Calculate HMACMD5 hash: HMACMD5(secret_key, uri)
    hmac_digest = hmac.new(secret_key.encode('utf-8'), uri.encode('utf-8'), hashlib.md5).digest()
    computed_hash_string = base64.b64encode(hmac_digest).decode('utf-8')
    
    # Set up the Authorization header
    headers = {
        "Authorization": f"Bearer {api_key}:{computed_hash_string}"
    }
    
    # Make the POST request (empty body)
    response = requests.post(uri, headers=headers)
    response.raise_for_status()  # Raise exception if an error occurred
    
    # Return the JSON response containing the token details
    return response.json()

def get_symptoms() -> list:
    """
    Load the list of symptoms from a local JSON file.

    This function reads the symptoms data from the JSON file located at
    "app/services/symptoms.json" and returns it as a list.

    :return: A list of symptoms, where each symptom is represented as a dictionary.
    :raises FileNotFoundError: If the symptoms file is not found at the specified path.
    :raises json.JSONDecodeError: If the file content is not valid JSON.
    """
    file_path = "app/services/symptoms.json"
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Symptoms file not found at path: {file_path}")
    
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    
    return data

def get_specialisations(
    symptoms: list[int],
    gender: str,
    year_of_birth: int,
    language: str = "en-gb",
    response_format: str = "json"
) -> list:
    """
    Retrieve a list of suggested specialisations based on symptoms, gender, and year of birth.

    Parameters:
        symptoms (list[int]): A list of symptom IDs (e.g., [10, 11, 12]). This will be JSON encoded.
        gender (str): The patient's gender. Expected values: "male" or "female".
        year_of_birth (int): The patient's year of birth.

    Returns:
        list: A list of specialisation dictionaries, each containing an "ID", "Name", and "Accuracy".

    Raises:
        HTTPError: If the API call fails with a non-200 status code.
    """
    token = get_access_token(settings.API_KEY_MEDICAL_API, settings.SECRET_KEY_MEDICAL_API)["Token"]
    url = "https://healthservice.priaid.ch/diagnosis/specialisations"
    
    # Build query parameters. The 'symptoms' parameter must be a JSON encoded list.
    params = {
        "token": token,
        "language": language,
        "symptoms": json.dumps(symptoms),
        "gender": gender,
        "year_of_birth": year_of_birth,
        "format": response_format,
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    return response.json()