"""
Document service for loading and processing medical documents from JSON.
"""
import json
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
import config


class DocumentService:
    """Service for loading and managing medical documents."""
    
    def __init__(self):
        """Initialize the document service."""
        self.diseases: List[Dict[str, Any]] = []
        self.documents: List[Document] = []
    
    def load_diseases(self, file_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Load diseases from JSON file.
        
        Args:
            file_path: Path to JSON file. Defaults to diseases.json in data directory.
            
        Returns:
            List of disease dictionaries
        """
        if file_path is None:
            file_path = config.DISEASES_FILE
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.diseases = json.load(f)
            return self.diseases
        except FileNotFoundError:
            raise FileNotFoundError(f"Diseases file not found: {file_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in diseases file: {file_path}")
    
    def create_documents_from_diseases(self) -> List[Document]:
        """
        Create LangChain Document objects from diseases.
        
        Returns:
            List of Document objects ready for embedding
        """
        if not self.diseases:
            self.load_diseases()
        
        self.documents = []
        
        for disease in self.diseases:
            # Create main disease document
            content = self._format_disease_content(disease)
            doc = Document(
                page_content=content,
                metadata={
                    "disease": disease.get("disease"),
                    "type": "disease_overview",
                    "symptoms": disease.get("symptoms", [])
                }
            )
            self.documents.append(doc)
            
            # Create symptom document for each disease
            symptoms_content = self._format_symptoms_content(disease)
            symptoms_doc = Document(
                page_content=symptoms_content,
                metadata={
                    "disease": disease.get("disease"),
                    "type": "symptoms",
                    "symptoms": disease.get("symptoms", [])
                }
            )
            self.documents.append(symptoms_doc)
            
            # Create diagnostic questions document
            questions_content = self._format_diagnostic_questions_content(disease)
            questions_doc = Document(
                page_content=questions_content,
                metadata={
                    "disease": disease.get("disease"),
                    "type": "diagnostic_questions",
                    "recommended_questions": disease.get("recommended_questions", [])
                }
            )
            self.documents.append(questions_doc)
            
            # Create treatments document
            treatments_content = self._format_treatments_content(disease)
            treatments_doc = Document(
                page_content=treatments_content,
                metadata={
                    "disease": disease.get("disease"),
                    "type": "treatments",
                    "treatments": disease.get("treatments", [])
                }
            )
            self.documents.append(treatments_doc)
        
        return self.documents
    
    @staticmethod
    def _format_disease_content(disease: Dict[str, Any]) -> str:
        """Format disease information for embedding."""
        disease_name = disease.get("disease", "Unknown")
        symptoms = ", ".join(disease.get("symptoms", []))
        return f"Disease: {disease_name}. Symptoms include: {symptoms}."
    
    @staticmethod
    def _format_symptoms_content(disease: Dict[str, Any]) -> str:
        """Format symptom information for embedding."""
        disease_name = disease.get("disease", "Unknown")
        symptoms = disease.get("symptoms", [])
        symptoms_text = "\n".join([f"- {symptom}" for symptom in symptoms])
        return f"Symptoms of {disease_name}:\n{symptoms_text}"
    
    @staticmethod
    def _format_diagnostic_questions_content(disease: Dict[str, Any]) -> str:
        """Format diagnostic questions for embedding."""
        disease_name = disease.get("disease", "Unknown")
        questions = disease.get("recommended_questions", [])
        questions_text = "\n".join([f"- {question}" for question in questions])
        return f"Diagnostic questions for {disease_name}:\n{questions_text}"
    
    @staticmethod
    def _format_treatments_content(disease: Dict[str, Any]) -> str:
        """Format treatment information for embedding."""
        disease_name = disease.get("disease", "Unknown")
        treatments = disease.get("treatments", [])
        treatments_text = "\n".join([f"- {treatment}" for treatment in treatments])
        return f"Treatments for {disease_name}:\n{treatments_text}"
    
    def get_disease_by_name(self, disease_name: str) -> Optional[Dict[str, Any]]:
        """
        Get disease information by disease name.
        
        Args:
            disease_name: Name of the disease
            
        Returns:
            Disease dictionary or None if not found
        """
        if not self.diseases:
            self.load_diseases()
        
        for disease in self.diseases:
            if disease.get("disease", "").lower() == disease_name.lower():
                return disease
        return None
    
    def get_all_diseases(self) -> List[str]:
        """
        Get list of all available disease names.
        
        Returns:
            List of disease names
        """
        if not self.diseases:
            self.load_diseases()
        
        return [disease.get("disease") for disease in self.diseases if disease.get("disease")]


# Global document service instance
_document_service: Optional[DocumentService] = None


def get_document_service() -> DocumentService:
    """Get or create the global document service instance."""
    global _document_service
    if _document_service is None:
        _document_service = DocumentService()
    return _document_service
