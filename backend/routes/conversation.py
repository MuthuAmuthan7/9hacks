"""
API routes for medical consultation conversation.
"""
import uuid
from fastapi import APIRouter, HTTPException
from backend.agents.patient_agent import create_patient_agent
from backend.agents.evaluation_agent import create_evaluation_agent
from backend.services.rag import get_rag_service
from backend.models.case_model import ConversationMessage
from backend.schemas import (
    StartCaseRequest,
    StartCaseResponse,
    DoctorInputRequest,
    DoctorInputResponse,
    EvaluateRequest,
    EvaluateResponse,
)

# Create router
router = APIRouter(prefix="/api", tags=["conversation"])

# In-memory storage for active cases (in production, use a database)
ACTIVE_CASES: dict = {}
CONVERSATIONS: dict = {}


@router.post(
    "/start_case",
    response_model=StartCaseResponse,
    summary="Start a new medical case",
    description="Create a new simulated patient case for the doctor to diagnose"
)
def start_case(request: StartCaseRequest = StartCaseRequest()):
    """
    Start a new medical case.
    
    Returns:
        case_id: Unique identifier for this case
        disease_hidden: True (the disease is hidden from the doctor)
        initial_message: Patient's opening statement
    """
    try:
        # Get RAG service and select a random disease
        rag_service = get_rag_service()
        rag_service.initialize()
        
        diseases = rag_service.get_available_diseases()
        if not diseases:
            raise HTTPException(
                status_code=500,
                detail="No diseases available in knowledge base"
            )
        
        # Select a random disease
        import random
        disease_name = random.choice(diseases)
        disease_info = rag_service.get_disease_information(disease_name)
        
        if not disease_info:
            raise HTTPException(
                status_code=500,
                detail=f"Could not load information for disease: {disease_name}"
            )
        
        # Create case ID
        case_id = str(uuid.uuid4())
        
        # Create patient agent
        patient = create_patient_agent(disease_info)
        ACTIVE_CASES[case_id] = {
            "patient": patient,
            "disease_info": disease_info,
            "created_at": __import__('datetime').datetime.utcnow()
        }
        
        # Initialize conversation
        CONVERSATIONS[case_id] = []
        
        # Generate initial patient message
        initial_prompt = "Please introduce yourself and tell me what brings you here today."
        initial_response = patient.respond_to_doctor(initial_prompt)
        
        # Add to conversation history
        CONVERSATIONS[case_id].append(
            ConversationMessage(role="patient", content=initial_response)
        )
        
        return StartCaseResponse(
            case_id=case_id,
            disease_hidden=True,
            initial_message=initial_response
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start case: {str(e)}"
        )


@router.post(
    "/doctor_input",
    response_model=DoctorInputResponse,
    summary="Send doctor input to patient",
    description="Send doctor's question or statement to the patient AI"
)
def doctor_input(request: DoctorInputRequest):
    """
    Process doctor input and get patient response.
    
    Args:
        case_id: ID of the case
        doctor_text: Doctor's question or statement
        
    Returns:
        patient_response: AI patient's response
        conversation_length: Number of turns so far
    """
    case_id = request.case_id
    doctor_text = request.doctor_text
    
    # Validate case exists
    if case_id not in ACTIVE_CASES:
        raise HTTPException(
            status_code=404,
            detail=f"Case not found: {case_id}"
        )
    
    if not doctor_text or not doctor_text.strip():
        raise HTTPException(
            status_code=400,
            detail="doctor_text is required and cannot be empty"
        )
    
    try:
        # Get active case
        case_data = ACTIVE_CASES[case_id]
        patient = case_data["patient"]
        
        # Add doctor message to conversation
        doctor_message = ConversationMessage(
            role="doctor",
            content=doctor_text
        )
        CONVERSATIONS[case_id].append(doctor_message)
        
        # Get patient response
        patient_response = patient.respond_to_doctor(doctor_text)
        
        # Add patient response to conversation
        patient_message = ConversationMessage(
            role="patient",
            content=patient_response
        )
        CONVERSATIONS[case_id].append(patient_message)
        
        return DoctorInputResponse(
            case_id=case_id,
            patient_response=patient_response,
            conversation_length=len(CONVERSATIONS[case_id])
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process doctor input: {str(e)}"
        )


@router.post(
    "/evaluate",
    response_model=EvaluateResponse,
    summary="Evaluate doctor's performance",
    description="Analyze the conversation and score the doctor's diagnostic and communication skills"
)
def evaluate(request: EvaluateRequest):
    """
    Evaluate the doctor's performance in the consultation.
    
    Args:
        case_id: ID of the case to evaluate
        
    Returns:
        evaluation: EvaluationResult with scores and feedback
        disease_revealed: The actual disease the patient had
    """
    case_id = request.case_id
    
    # Validate case exists
    if case_id not in ACTIVE_CASES:
        raise HTTPException(
            status_code=404,
            detail=f"Case not found: {case_id}"
        )
    
    if case_id not in CONVERSATIONS:
        raise HTTPException(
            status_code=400,
            detail=f"No conversation found for case: {case_id}"
        )
    
    try:
        # Get case data
        case_data = ACTIVE_CASES[case_id]
        disease_info = case_data["disease_info"]
        conversation = CONVERSATIONS[case_id]
        
        # Check if we have a conversation to evaluate
        if len(conversation) < 2:
            raise HTTPException(
                status_code=400,
                detail="Not enough conversation to evaluate. Doctor must ask at least one question."
            )
        
        # Create evaluation agent and evaluate
        evaluator = create_evaluation_agent()
        evaluation_result = evaluator.evaluate_consultation(disease_info, conversation)
        
        # Clean up the case (optional - remove after evaluation)
        # del ACTIVE_CASES[case_id]
        # del CONVERSATIONS[case_id]
        
        return EvaluateResponse(
            case_id=case_id,
            evaluation=evaluation_result,
            disease_revealed=disease_info.get("disease", "Unknown")
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to evaluate case: {str(e)}"
        )


@router.get(
    "/cases/{case_id}",
    summary="Get case details",
    description="Retrieve details about a specific case"
)
def get_case(case_id: str):
    """Get details about a case."""
    if case_id not in ACTIVE_CASES:
        raise HTTPException(
            status_code=404,
            detail=f"Case not found: {case_id}"
        )
    
    case_data = ACTIVE_CASES[case_id]
    conversation = CONVERSATIONS.get(case_id, [])
    
    return {
        "case_id": case_id,
        "created_at": case_data["created_at"].isoformat(),
        "conversation_length": len(conversation),
        "conversation": [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in conversation
        ]
    }


@router.get(
    "/health",
    summary="Health check",
    description="Check if the API is running"
)
def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "Medical AI Consultation API is running"
    }
