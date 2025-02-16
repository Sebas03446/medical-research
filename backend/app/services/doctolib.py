import os, json

def get_doctolib_specialisations() -> list:
    """
    Retrieve a list of specialisations.
    
    Returns:
        list: A list of specialisation dictionaries, each containing an "ID" and "Name".
        
    Raises:
        HTTPError: If the API call fails with a non-200 status code.
    """
    specialisations = ['Médecin généraliste', 'Cabinet médical', 'Médecin morphologue et anti-âge', 'Cabinet pluridisciplinaire', 'Centre de santé', 'Maison de santé', 'Infectiologue', 'Pharmacie', 'Centre laser et esthétique', 'Interne en médecine', 'Ophtalmologue', "Établissement de Santé Privé d'Intérêt Collectif (ESPIC)", "Centre d'ophtalmologie", 'Cabinet médical et dentaire', 'Centre médical et dentaire', 'Allergologue', 'Pneumologue', 'Pédiatre', 'ORL', 'Dermatologue et vénérologue', 'Hôpital public', 'Spécialiste en médecine interne', 'Psychologue']
    
    return specialisations
def standardize_doctor(doctor: dict) -> dict:
    """
    Standardizes a doctor's dictionary keys to English.

    Changes:
      - 'nom' becomes 'name'
      - 'horaire_contact' becomes 'contact_info'
      - 'tarif' becomes 'pricing'

    Other keys remain unchanged.

    Parameters:
        doctor (dict): The original doctor dictionary with French keys.

    Returns:
        dict: A new dictionary with standardized English keys.
    """
    return {
        "description": doctor.get("description", ""),
        "expertise": doctor.get("expertise", ""),
        "contact_info": doctor.get("horaire_contact", ""),
        "image": doctor.get("image", ""),
        "name": doctor.get("nom", ""),
        "phones": doctor.get("phones", []),
        "pricing": doctor.get("tarif", ""),
        "url": doctor.get("url", "")
    }

def get_doctors(specialisation_name: str) -> list:
    """
    Retrieve a list of doctors based on a given specialisation.

    Parameters:
        specialisation_name (str): The name of the specialisation.

    Returns:
        list: A list of doctor dictionaries for the given specialisation.
              Returns an empty list if no doctors are found.
    """
    file_path = "backend/app/services/grouped_by_specialite.json"
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Symptoms file not found at path: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    normalized_spec = specialisation_name.strip()

    for key, doctors in data.items():
        if key.strip() == normalized_spec:
            return [standardize_doctor(doctor) for doctor in doctors]

    return []

    return []
