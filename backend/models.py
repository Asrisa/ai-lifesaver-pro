from pydantic import BaseModel, Field
from typing import List, Optional

class UserContext(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = Field(default=None, description="male|female|other")
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None

class ConditionAssessment(BaseModel):
    condition_type: str
    severity: str                  # low|moderate|high|critical
    confidence: float
    red_flags: List[str]
    recommended_actions: List[str]
    self_care_advice: Optional[str] = None
    nearest_hospitals: Optional[List[dict]] = None
    weather_context: Optional[dict] = None

class SymptomInput(BaseModel):
    symptoms: str
    user: Optional[UserContext] = None

class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = "alloy"

