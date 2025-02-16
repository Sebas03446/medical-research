from typing import List, Dict
from ..tools.base import Tool

class MedicalService:
    @Tool(
        name="get_symptoms",
        description="Get list of available symptoms from the medical database"
    )
    async def get_symptoms(self) -> List[Dict]:
        """Get list of all available symptoms"""
        # Implementation
        pass

    @Tool(
        name="get_specializations",
        description="Get recommended medical specializations based on symptoms"
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