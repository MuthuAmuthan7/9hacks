from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class CaseModel(BaseModel):
    """Medical case model for doctor-patient simulation."""
    case_id: str = Field(..., description="Unique case identifier")
    disease: str = Field(..., description="Disease name (hidden from doctor)")
    symptoms: List[str] = Field(..., description="Patient symptoms")
    recommended_questions: List[str] = Field(..., description="Questions doctor should ask")
    treatments: List[str] = Field(..., description="Recommended treatments")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ConversationMessage(BaseModel):
    """Conversation message model."""
    role: str = Field(..., description="Either 'doctor' or 'patient'")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EvaluationResult(BaseModel):
    """Doctor evaluation result."""
    diagnostic_score: float = Field(..., ge=0, le=10, description="Quality of diagnostic questions (0-10)")
    symptom_understanding_score: float = Field(..., ge=0, le=10, description="Understanding of symptoms (0-10)")
    treatment_score: float = Field(..., ge=0, le=10, description="Treatment recommendation accuracy (0-10)")
    communication_score: float = Field(..., ge=0, le=10, description="Communication skill (0-10)")
    overall_score: float = Field(..., ge=0, le=100, description="Overall score (0-100)")
    feedback: str = Field(..., description="Detailed feedback on doctor performance")
    asked_questions: List[str] = Field(default_factory=list, description="Questions doctor asked")
    correct_questions: List[str] = Field(default_factory=list, description="Correct diagnostic questions asked")
    missing_questions: List[str] = Field(default_factory=list, description="Important questions not asked")
