from typing import List, Dict
from ..tools.base import Tool


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
        # Implementation
        pass

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
        pass

