"""
Evaluation agent that evaluates doctor's diagnostic and communication skills.
"""
import json
from typing import List, Dict, Any, Optional
from langchain_groq import ChatGroq
from backend.prompts import EVALUATION_AGENT_SYSTEM_PROMPT, EVALUATION_PROMPT_TEMPLATE
from backend.models.case_model import EvaluationResult, ConversationMessage
import config


class EvaluationAgent:
    """Agent that evaluates doctor's performance in patient consultation."""
    
    def __init__(self):
        """Initialize the evaluation agent."""
        self.llm = ChatGroq(
            model=config.GROQ_MODEL,
            temperature=0.3,
            api_key=config.GROQ_API_KEY
        )
    
    def evaluate_consultation(
        self,
        disease_info: Dict[str, Any],
        conversation: List[ConversationMessage]
    ) -> EvaluationResult:
        """
        Evaluate a doctor's consultation based on conversation.
        
        Args:
            disease_info: Information about the disease being simulated
            conversation: List of conversation messages between doctor and patient
            
        Returns:
            EvaluationResult with scores and feedback
        """
        # Format conversation for evaluation
        conversation_text = self._format_conversation(conversation)
        
        # Extract information
        disease = disease_info.get("disease", "Unknown")
        symptoms = disease_info.get("symptoms", [])
        recommended_questions = disease_info.get("recommended_questions", [])
        treatments = disease_info.get("treatments", [])
        
        # Create evaluation prompt
        evaluation_prompt = EVALUATION_PROMPT_TEMPLATE.format(
            disease=disease,
            symptoms=", ".join(symptoms),
            recommended_questions="\n".join([f"- {q}" for q in recommended_questions]),
            treatments="\n".join([f"- {t}" for t in treatments]),
            conversation=conversation_text
        )

        # Get evaluation from LLM
        try:
            messages = [
                {"role": "system", "content": EVALUATION_AGENT_SYSTEM_PROMPT},
                {"role": "user", "content": evaluation_prompt}
            ]
            response = self.llm.invoke(messages)
            response_text = response.content.strip()
            
            # Parse JSON response
            evaluation_json = self._extract_json(response_text)
            
            # Validate and create result
            result = self._create_evaluation_result(evaluation_json, conversation)
            return result
        
        except Exception as e:
            # Return fallback evaluation on error
            return self._create_fallback_evaluation(conversation, disease_info)
    
    def _format_conversation(self, conversation: List[ConversationMessage]) -> str:
        """Format conversation for display."""
        formatted = []
        for msg in conversation:
            role = msg.role.capitalize()
            content = msg.content
            formatted.append(f"{role}: {content}")
        return "\n".join(formatted)
    
    def _extract_json(self, text: str) -> Dict[str, Any]:
        """
        Extract JSON from response text.
        
        Args:
            text: Response text that should contain JSON
            
        Returns:
            Parsed JSON dictionary
        """
        # Try to find JSON in the text
        import re
        
        # Look for JSON object
        json_pattern = r'\{.*\}'
        matches = re.findall(json_pattern, text, re.DOTALL)
        
        if matches:
            try:
                return json.loads(matches[-1])
            except json.JSONDecodeError:
                pass
        
        # If no JSON found, try parsing the whole text
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            raise ValueError("Could not extract valid JSON from response")
    
    def _create_evaluation_result(
        self,
        evaluation_json: Dict[str, Any],
        conversation: List[ConversationMessage]
    ) -> EvaluationResult:
        """
        Create an EvaluationResult from JSON response.
        
        Args:
            evaluation_json: Parsed evaluation JSON
            conversation: Original conversation
            
        Returns:
            EvaluationResult object
        """
        # Extract doctor questions from conversation
        doctor_questions = [
            msg.content for msg in conversation
            if msg.role.lower() == "doctor"
        ]
        
        # Safely extract scores, defaulting to 0 if not present
        diagnostic_score = float(evaluation_json.get("diagnostic_score", 0))
        symptom_understanding_score = float(
            evaluation_json.get("symptom_understanding_score", 0)
        )
        treatment_score = float(evaluation_json.get("treatment_score", 0))
        communication_score = float(evaluation_json.get("communication_score", 0))
        
        # Calculate overall score
        overall_score = (
            (diagnostic_score + symptom_understanding_score + 
             treatment_score + communication_score) / 4
        ) * 10
        
        # Ensure scores are within bounds
        diagnostic_score = min(10, max(0, diagnostic_score))
        symptom_understanding_score = min(10, max(0, symptom_understanding_score))
        treatment_score = min(10, max(0, treatment_score))
        communication_score = min(10, max(0, communication_score))
        overall_score = min(100, max(0, overall_score))
        
        return EvaluationResult(
            diagnostic_score=diagnostic_score,
            symptom_understanding_score=symptom_understanding_score,
            treatment_score=treatment_score,
            communication_score=communication_score,
            overall_score=overall_score,
            feedback=evaluation_json.get(
                "feedback",
                "Evaluation completed. Review the scores for detailed feedback."
            ),
            asked_questions=doctor_questions,
            correct_questions=evaluation_json.get("correct_questions", []),
            missing_questions=evaluation_json.get("missing_questions", [])
        )
    
    def _create_fallback_evaluation(
        self,
        conversation: List[ConversationMessage],
        disease_info: Dict[str, Any]
    ) -> EvaluationResult:
        """
        Create a basic evaluation when LLM processing fails.
        
        Args:
            conversation: Conversation history
            disease_info: Disease information
            
        Returns:
            Basic EvaluationResult
        """
        doctor_questions = [
            msg.content for msg in conversation
            if msg.role.lower() == "doctor"
        ]
        
        num_questions = len(doctor_questions)
        
        # Simple scoring based on conversation length
        diagnostic_score = min(10, num_questions / 2)
        symptom_understanding_score = 5.0
        treatment_score = 3.0 if num_questions > 5 else 2.0
        communication_score = 6.0
        overall_score = (
            (diagnostic_score + symptom_understanding_score +
             treatment_score + communication_score) / 4
        ) * 10
        
        return EvaluationResult(
            diagnostic_score=diagnostic_score,
            symptom_understanding_score=symptom_understanding_score,
            treatment_score=treatment_score,
            communication_score=communication_score,
            overall_score=overall_score,
            feedback=(
                f"Based on {num_questions} questions asked. "
                "The doctor covered the conversation adequately. "
                "Review the questions asked and missing questions to improve."
            ),
            asked_questions=doctor_questions,
            correct_questions=[],
            missing_questions=disease_info.get("recommended_questions", [])[:3]
        )


def create_evaluation_agent() -> EvaluationAgent:
    """Factory function to create an evaluation agent."""
    return EvaluationAgent()
