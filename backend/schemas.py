"""
API request and response schemas for the Medical AI Consultation System.

This module contains all Pydantic models used for API request/response validation.
Organized by feature/endpoint for clarity.
"""

from typing import List
from pydantic import BaseModel, Field
from backend.models.case_model import EvaluationResult


# ============================================================================
# CASE MANAGEMENT SCHEMAS
# ============================================================================

class StartCaseRequest(BaseModel):
    """Request to start a new medical case."""
    pass


class StartCaseResponse(BaseModel):
    """Response when starting a new medical case with patient greeting."""
    case_id: str = Field(
        ...,
        description="Unique identifier for this medical case",
        example="550e8400-e29b-41d4-a716-446655440000"
    )
    disease_hidden: bool = Field(
        ...,
        description="Whether the disease is hidden from the doctor",
        example=True
    )
    initial_message: str = Field(
        ...,
        description="Patient's initial opening message/complaint",
        example="Doctor, I've been feeling unwell for the past 3 days..."
    )


# ============================================================================
# CONVERSATION SCHEMAS
# ============================================================================

class DoctorInputRequest(BaseModel):
    """Request to send doctor input (question or statement) to the patient."""
    case_id: str = Field(
        ...,
        description="Unique case identifier",
        example="550e8400-e29b-41d4-a716-446655440000"
    )
    doctor_text: str = Field(
        ...,
        min_length=1,
        description="Doctor's question or statement to the patient (cannot be empty)",
        example="How long have you had these symptoms?"
    )

    class Config:
        """Schema configuration."""
        json_schema_extra = {
            "example": {
                "case_id": "550e8400-e29b-41d4-a716-446655440000",
                "doctor_text": "How long have you had fever?"
            }
        }


class DoctorInputResponse(BaseModel):
    """Response containing patient's reply to doctor's input."""
    case_id: str = Field(
        ...,
        description="Case identifier",
        example="550e8400-e29b-41d4-a716-446655440000"
    )
    patient_response: str = Field(
        ...,
        description="AI patient's response to doctor's question",
        example="The fever comes and goes, but it's been constant for about 3 days..."
    )
    conversation_length: int = Field(
        ...,
        ge=0,
        description="Total number of messages in conversation so far",
        example=4
    )

    class Config:
        """Schema configuration."""
        json_schema_extra = {
            "example": {
                "case_id": "550e8400-e29b-41d4-a716-446655440000",
                "patient_response": "Yes, it started on Monday evening...",
                "conversation_length": 4
            }
        }


# ============================================================================
# EVALUATION SCHEMAS
# ============================================================================

class EvaluateRequest(BaseModel):
    """Request to evaluate the doctor's consultation performance."""
    case_id: str = Field(
        ...,
        description="Case identifier to evaluate",
        example="550e8400-e29b-41d4-a716-446655440000"
    )

    class Config:
        """Schema configuration."""
        json_schema_extra = {
            "example": {
                "case_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }


class EvaluateResponse(BaseModel):
    """Response containing doctor evaluation results and scores."""
    case_id: str = Field(
        ...,
        description="Case identifier",
        example="550e8400-e29b-41d4-a716-446655440000"
    )
    evaluation: EvaluationResult = Field(
        ...,
        description="Detailed evaluation results with scores and feedback"
    )
    disease_revealed: str = Field(
        ...,
        description="The actual disease name that was hidden from doctor",
        example="Influenza"
    )

    class Config:
        """Schema configuration."""
        json_schema_extra = {
            "example": {
                "case_id": "550e8400-e29b-41d4-a716-446655440000",
                "evaluation": {
                    "diagnostic_score": 8.5,
                    "symptom_understanding_score": 7.0,
                    "treatment_score": 8.0,
                    "communication_score": 9.0,
                    "overall_score": 82.5,
                    "feedback": "Good diagnostic approach..."
                },
                "disease_revealed": "Influenza"
            }
        }


# ============================================================================
# UTILITY SCHEMAS
# ============================================================================

class CaseDetailsResponse(BaseModel):
    """Response containing full case details including conversation history."""
    case_id: str = Field(
        ...,
        description="Case identifier",
        example="550e8400-e29b-41d4-a716-446655440000"
    )
    created_at: str = Field(
        ...,
        description="ISO format timestamp when case was created",
        example="2026-03-14T10:30:00"
    )
    conversation_length: int = Field(
        ...,
        ge=0,
        description="Total number of messages in conversation",
        example=8
    )
    conversation: List[dict] = Field(
        default_factory=list,
        description="List of all conversation messages"
    )


class HealthCheckResponse(BaseModel):
    """Response for health check endpoint."""
    status: str = Field(
        ...,
        description="Health status",
        example="healthy"
    )
    message: str = Field(
        ...,
        description="Status message",
        example="Medical AI Consultation API is running"
    )


class RootResponse(BaseModel):
    """Response from root API endpoint."""
    name: str = Field(
        ...,
        description="API name",
        example="Medical AI Consultation System"
    )
    description: str = Field(
        ...,
        description="API description",
        example="Evaluate doctor's medical knowledge through AI patient simulation"
    )
    version: str = Field(
        ...,
        description="API version",
        example="1.0.0"
    )
    endpoints: dict = Field(
        default_factory=dict,
        description="Available API endpoints"
    )
    docs: str = Field(
        ...,
        description="URL to interactive API documentation",
        example="/docs"
    )
    redoc: str = Field(
        ...,
        description="URL to ReDoc documentation",
        example="/redoc"
    )
