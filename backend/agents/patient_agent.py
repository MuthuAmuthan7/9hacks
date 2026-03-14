"""
Patient agent that simulates a patient in medical diagnosis roleplay.
"""
import random
from typing import List, Dict, Any, Optional
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
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

        # Conversation history for context
        self.conversation_history: List[Dict[str, str]] = []

        # Initialize LLM (Groq)
        self.llm = ChatGroq(
            model=config.GROQ_MODEL,
            temperature=0.7,
            api_key=config.GROQ_API_KEY
        )

        # Create patient background
        self.patient_background = self._create_patient_background()
        self.system_message = PATIENT_AGENT_SYSTEM_PROMPT + "\n\n" + self.patient_background

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

    def respond_to_doctor(self, doctor_input: str) -> str:
        """
        Generate patient response to doctor's input using full conversation history.

        Args:
            doctor_input: Doctor's question or statement

        Returns:
            Patient's response
        """
        try:
            # Build messages with full conversation history
            messages = [SystemMessage(content=self.system_message)]

            for msg in self.conversation_history:
                if msg["role"] == "doctor":
                    messages.append(HumanMessage(content=msg["content"]))
                else:
                    messages.append(AIMessage(content=msg["content"]))

            messages.append(HumanMessage(content=doctor_input))

            response = self.llm.invoke(messages)
            response_text = response.content.strip()

            # Store in history
            self.conversation_history.append({"role": "doctor", "content": doctor_input})
            self.conversation_history.append({"role": "patient", "content": response_text})

            return response_text
        except Exception as e:
            print(f"LLM call failed: {e}")
            fallback = self._rule_based_response(doctor_input)
            self.conversation_history.append({"role": "doctor", "content": doctor_input})
            self.conversation_history.append({"role": "patient", "content": fallback})
            return fallback

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
        matching_symptoms = [s for s in self.symptoms if s.lower() in doctor_lower]
        if matching_symptoms:
            symptom = matching_symptoms[0]
            responses = [
                f"Yes, I've been having {symptom}. It started a few days ago and it's been bothering me.",
                f"Actually yes, the {symptom} has been quite bad. It comes and goes throughout the day.",
                f"Yes doctor, I do have {symptom}. It's been getting worse over the past few days.",
            ]
            return random.choice(responses)

        # Duration questions
        if any(w in doctor_lower for w in ["how long", "duration", "how many days", "when did", "started"]):
            return f"It's been about {self._estimate_duration()} now. I was hoping it would go away on its own but it hasn't."

        # Symptom description questions
        if any(w in doctor_lower for w in ["what symptoms", "what are you feeling", "what brings you", "what's wrong", "complain"]):
            main_symptoms = ", ".join(self.symptoms[:3])
            other = f" I also have some {self.symptoms[3]}." if len(self.symptoms) > 3 else ""
            return f"I've been having {main_symptoms}.{other} It's really affecting my daily life."

        # Severity questions
        if any(w in doctor_lower for w in ["severe", "scale", "how bad", "intensity", "rate"]):
            return f"I'd say it's {self._estimate_severity()}. Some days are worse than others, but overall it's been hard to manage."

        # Medication questions
        if any(w in doctor_lower for w in ["medicine", "medication", "drug", "treatment", "taking any", "prescribed"]):
            return "No, I haven't taken any medications for this yet. I wanted to get a proper diagnosis first."

        # History questions
        if any(w in doctor_lower for w in ["history", "before", "past", "previous", "family"]):
            return "Not that I can recall. This is the first time I'm experiencing something like this."

        # Allergy questions
        if any(w in doctor_lower for w in ["allerg", "react"]):
            return "No known allergies that I'm aware of, doctor."

        # Yes/no style questions - try to match based on symptoms
        if any(w in doctor_lower for w in ["do you have", "are you experiencing", "have you had", "any"]):
            for symptom in self.symptoms:
                words = symptom.lower().split()
                if any(w in doctor_lower for w in words if len(w) > 3):
                    return f"Yes, I do have {symptom}. It's been part of what I've been dealing with."
            return "No, I don't think I've had that."

        # Default - give a helpful response instead of confusion
        symptoms_str = ", ".join(self.symptoms[:2])
        return f"Well, my main concern is the {symptoms_str}. Is there anything specific you'd like to know about my condition?"

    def get_disease_info(self) -> Dict[str, Any]:
        """Get the disease information (for evaluation purposes)."""
        return self.disease_info

    @staticmethod
    def _estimate_duration() -> str:
        """Estimate duration of illness."""
        return random.choice(["3 days", "about a week", "4-5 days", "nearly a week"])

    @staticmethod
    def _estimate_severity() -> str:
        """Estimate severity of illness."""
        return random.choice(["moderate", "moderate to bad", "quite uncomfortable"])

    @staticmethod
    def _assign_patient_age() -> int:
        """Assign a patient age."""
        return random.choice([28, 32, 35, 40, 45, 50, 55])

    @staticmethod
    def _assign_patient_gender() -> str:
        """Assign a patient gender."""
        return random.choice(["male", "female"])


def create_patient_agent(disease_info: Dict[str, Any]) -> PatientAgent:
    """
    Factory function to create a patient agent.

    Args:
        disease_info: Disease information dictionary

    Returns:
        PatientAgent instance
    """
    return PatientAgent(disease_info)

