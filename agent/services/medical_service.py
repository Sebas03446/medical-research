from typing import List, Dict
from ..tools.base import Tool

from backend.app.services.medical_api import get_symptoms, get_specialisations


class MedicalService:
    @Tool(
        name="get_symptoms",
        description="""
        Retrieves a comprehensive list of medical symptoms from the database. 
        This tool should be used when:
        1. The user asks about available symptoms
        2. You need to look up specific symptom information
        3. You're helping diagnose a condition and need to check symptoms
        
        The tool returns a list of symptoms with their IDs and detailed descriptions.
        Note: This tool does not diagnose conditions, it only provides symptom information.
        """
    )
    async def get_symptoms(self) -> List[Dict]:
        """Get list of all available symptoms"""
        try:
            symptoms = get_symptoms()
            return symptoms
            
        except Exception as e:
            # Log error and return empty list or raise depending on your error handling strategy
            print(f"Error fetching symptoms: {str(e)}")
            return []

    @Tool(
        name="get_specializations",
        description="""
        Recommends medical specializations based on symptoms and patient information.
        This tool should be used when:
        1. A user describes specific symptoms and needs specialist recommendations
        2. You need to determine which type of doctor would be most appropriate
        
        Required parameters:
        - symptom_ids: List of symptom IDs from the get_symptoms tool
        - age: Patient's age (important for age-specific recommendations)
        - gender: Patient's gender (relevant for certain specializations)
        
        The tool returns a ranked list of medical specializations with confidence scores.
        Note: These are suggestions only and not definitive medical advice.
        """
    )
    async def get_specializations(
        self, 
        symptom_ids: List[int],
        age: int,
        gender: str
    ) -> List[Dict]:
        """
        Get specialization recommendations.
        :param symptom_ids: List of symptom IDs to analyze
        :param age: Patient's age
        :param gender: Patient's gender (male/female)
        """
        # Implementation
        try:
            # Input validation
            if not symptom_ids:
                raise ValueError("At least one symptom ID is required")
            
            if not isinstance(symptom_ids, list):
                raise ValueError("symptom_ids must be a list")
            
            if not all(isinstance(id, int) for id in symptom_ids):
                raise ValueError("All symptom IDs must be integers")
            
            if not isinstance(age, int) or age < 0 or age > 120:
                raise ValueError("Invalid age value")
            
            if gender.lower() not in ['male', 'female']:
                raise ValueError("Gender must be 'male' or 'female'")
            
            # Calculate year of birth from age
            from datetime import datetime
            year_of_birth = datetime.now().year - age
            
            # Call backend function with validated parameters
            specializations = await get_specialisations(
                symptom_ids=symptom_ids,
                gender=gender.lower(),
                year_of_birth=year_of_birth
            )
            
            # Validate response format
            for spec in specializations:
                if not all(key in spec for key in ['id', 'name', 'confidence']):
                    raise ValueError("Invalid specialization format in response")
            
            return specializations
            
        except ValueError as ve:
            
            raise ve
        except Exception as e:
            
            print(f"Error fetching specializations: {str(e)}")
            return []

    def _validate_symptom_ids(self, symptom_ids: List[int]) -> bool:
        """Helper method to validate symptom IDs"""
        if not symptom_ids:
            return False
        return all(isinstance(id, int) and id > 0 for id in symptom_ids)

    def _validate_gender(self, gender: str) -> bool:
        """Helper method to validate gender"""
        return gender.lower() in ['male', 'female']

    def _validate_age(self, age: int) -> bool:
        """Helper method to validate age"""
        return isinstance(age, int) and 0 <= age <= 120
