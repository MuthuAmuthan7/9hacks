"""
RAG (Retrieval Augmented Generation) service for medical knowledge retrieval.
"""
from typing import List, Optional
from langchain_core.documents import Document
from backend.services.retriever_service import get_retriever_service
from backend.services.document_service import get_document_service


class RAGService:
    """Service for Retrieval Augmented Generation of medical knowledge."""
    
    def __init__(self):
        """Initialize the RAG service with retriever and document services."""
        self.retriever = get_retriever_service()
        self.document_service = get_document_service()
        self._initialized = False
    
    def initialize(self):
        """Initialize the RAG system by loading documents and setting up vector store."""
        if self._initialized:
            return
        
        try:
            # Load diseases from JSON
            self.document_service.load_diseases()
            
            # Create documents from diseases
            documents = self.document_service.create_documents_from_diseases()
            
            # Initialize retriever
            self.retriever.initialize()
            
            # Add documents to vector store
            self.retriever.add_documents(documents)
            
            self._initialized = True
        except Exception as e:
            raise RuntimeError(f"Failed to initialize RAG system: {str(e)}")
    
    def retrieve_medical_knowledge(self, query: str, k: int = 5) -> List[Document]:
        """
        Retrieve medical knowledge documents related to a query.
        
        Args:
            query: Query string (can be symptoms, questions, or treatments)
            k: Number of results to return
            
        Returns:
            List of relevant Document objects
        """
        if not self._initialized:
            self.initialize()
        
        try:
            results = self.retriever.search(query, k=k)
            return results
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve medical knowledge: {str(e)}")
    
    def retrieve_for_symptom(self, symptoms: List[str]) -> List[Document]:
        """
        Retrieve disease information based on symptoms.
        
        Args:
            symptoms: List of patient symptoms
            
        Returns:
            List of relevant disease documents
        """
        if not self._initialized:
            self.initialize()
        
        symptom_query = " ".join(symptoms)
        return self.retrieve_medical_knowledge(symptom_query, k=10)
    
    def retrieve_for_diagnostic_guidance(self, query: str) -> List[Document]:
        """
        Retrieve diagnostic guidance based on doctor's query.
        
        Args:
            query: Doctor's diagnostic query or question
            
        Returns:
            List of relevant diagnostic documents
        """
        if not self._initialized:
            self.initialize()
        
        return self.retrieve_medical_knowledge(query, k=5)
    
    def retrieve_treatment_info(self, condition: str) -> List[Document]:
        """
        Retrieve treatment information for a specific condition.
        
        Args:
            condition: Condition or disease name
            
        Returns:
            List of treatment documents
        """
        if not self._initialized:
            self.initialize()
        
        query = f"treatment for {condition}"
        return self.retrieve_medical_knowledge(query, k=5)
    
    def get_disease_information(self, disease_name: str) -> Optional[dict]:
        """
        Get complete disease information.
        
        Args:
            disease_name: Name of the disease
            
        Returns:
            Complete disease information dictionary
        """
        if not self._initialized:
            self.initialize()
        
        return self.document_service.get_disease_by_name(disease_name)
    
    def get_available_diseases(self) -> List[str]:
        """
        Get list of all available diseases in the system.
        
        Returns:
            List of disease names
        """
        if not self._initialized:
            self.initialize()
        
        return self.document_service.get_all_diseases()
    
    def clear_knowledge_base(self):
        """Clear all documents from the knowledge base."""
        try:
            self.retriever.clear_collection()
            self._initialized = False
        except Exception as e:
            raise RuntimeError(f"Failed to clear knowledge base: {str(e)}")


# Global RAG service instance
_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """Get or create the global RAG service instance."""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
