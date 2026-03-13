"""
Patient agent that simulates a patient in medical diagnosis roleplay.
"""
from typing import List, Dict, Any, Optional
from langchain.memory import ConversationBufferMemory
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from backend.prompts import PATIENT_AGENT_SYSTEM_PROMPT, PATIENT_BACKGROUND_TEMPLATE
import config


class PatientAgent:
    """Agent that simulates a patient during medical consultation."""
    
    def __init__(self, disease_info: Dict[str, Any]):
        """
        Initialize the patient agent.
        
        Args:
            disease_info: Dictionary containing disease, symptoms, etc.
        """
        self.disease_info = disease_info
        self.disease_name = disease_info.get("disease", "Unknown")
        self.symptoms = disease_info.get("symptoms", [])
        self.treatments = disease_info.get("treatments", [])
        self.recommended_questions = disease_info.get("recommended_questions", [])
        
        # Initialize LLM (Groq)
        self.llm = ChatGroq(
            model=config.GROQ_MODEL,
            temperature=0.7,
            api_key=config.GROQ_API_KEY
        )
        
        # Initialize memory for conversation
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Create patient background
        self.patient_background = self._create_patient_background()
        
        # Build the chain
        self.chain = self._build_chain()
    
    def _create_patient_background(self) -> str:
        """Create the patient background prompt."""
        symptoms_text = ", ".join(self.symptoms)
        duration = self._estimate_duration()
        severity = self._estimate_severity()
        age = self._assign_patient_age()
        gender = self._assign_patient_gender()
        
        background = PATIENT_BACKGROUND_TEMPLATE.format(
            gender=gender,
            age=age,
            symptoms=symptoms_text,
            duration=duration,
            severity=severity,
            disease=self.disease_name
        )
        return background
    
    def _build_chain(self) -> LLMChain:
        """Build the LLM chain for patient responses."""
        system_message = PATIENT_AGENT_SYSTEM_PROMPT + "\n\n" + self.patient_background
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", "{input}")
        ])
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        return chain
    
    def respond_to_doctor(self, doctor_input: str) -> str:
        """
        Generate patient response to doctor's input.
        
        Args:
            doctor_input: Doctor's question or statement
            
        Returns:
            Patient's response
        """
        try:
            # Check if doctor input is about symptoms
            response = self.chain.run(input=doctor_input)
            return response.strip()
        except Exception as e:
            # Fallback to rule-based response
            return self._rule_based_response(doctor_input)
    
    def _rule_based_response(self, doctor_input: str) -> str:
        """
        Generate rule-based response if LLM fails.
        
        Args:
            doctor_input: Doctor's question
            
        Returns:
            Simple rule-based response
        """
        doctor_lower = doctor_input.lower()
        
        # Check for symptom questions
        for symptom in self.symptoms:
            if symptom.lower() in doctor_lower:
                return f"Yes, I've been experiencing {symptom}. It started a few days ago."
        
        # Generic responses
        if "how" in doctor_lower and ("long" in doctor_lower or "duration" in doctor_lower):
            return "I've had these symptoms for about 3 days now."
        
        if "what" in doctor_lower or "when" in doctor_lower:
            symptoms_str = ", ".join(self.symptoms[:3])
            return f"I'm experiencing {symptoms_str}. It's been affecting me quite a bit."
        
        if "medicine" in doctor_lower or "medication" in doctor_lower or "treatment" in doctor_lower:
            return "I haven't taken any medications for this yet. I was waiting to see what you'd recommend."
        
        # Default response
        return "I'm not sure about that. Can you explain what you mean?"
    
    def get_disease_info(self) -> Dict[str, Any]:
        """Get the disease information (for evaluation purposes)."""
        return self.disease_info
    
    def reset_conversation(self):
        """Reset conversation memory."""
        self.memory.clear()
    
    @staticmethod
    def _estimate_duration() -> str:
        """Estimate duration of illness."""
        return "3 days"
    
    @staticmethod
    def _estimate_severity() -> str:
        """Estimate severity of illness."""
        return "moderate"
    
    @staticmethod
    def _assign_patient_age() -> int:
        """Assign a patient age."""
        return 35
    
    @staticmethod
    def _assign_patient_gender() -> str:
        """Assign a patient gender."""
        return "male"
    
    def _generate_simple_response(self, doctor_input: str) -> str:
        """
        Generate a simple response using direct LLM call.
        
        Args:
            doctor_input: Doctor's question
            
        Returns:
            Patient's response
        """
        prompt = f"""{PATIENT_AGENT_SYSTEM_PROMPT}

{self.patient_background}

Doctor: {doctor_input}
Patient:"""
        
        try:
            response = self.llm.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            # Final fallback
            return self._rule_based_response(doctor_input)


def create_patient_agent(disease_info: Dict[str, Any]) -> PatientAgent:
    """
    Factory function to create a patient agent.
    
    Args:
        disease_info: Disease information dictionary
        
    Returns:
        PatientAgent instance
    """
    return PatientAgent(disease_info)
