"""
System prompts module for Medical AI Consultation System.

This package contains all LLM system prompts organized by agent type:
- patient: Prompts for patient agent simulation
- evaluation: Prompts for doctor evaluation agent
"""

from backend.prompts.patient import (
    PATIENT_AGENT_SYSTEM_PROMPT,
    PATIENT_BACKGROUND_TEMPLATE,
)
from backend.prompts.evaluation import (
    EVALUATION_AGENT_SYSTEM_PROMPT,
    EVALUATION_PROMPT_TEMPLATE,
)

__all__ = [
    "PATIENT_AGENT_SYSTEM_PROMPT",
    "PATIENT_BACKGROUND_TEMPLATE",
    "EVALUATION_AGENT_SYSTEM_PROMPT",
    "EVALUATION_PROMPT_TEMPLATE",
]
