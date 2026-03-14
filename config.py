import os
from typing import Optional
from dotenv import load_dotenv

# Load .env file for local development (no-op if vars already set, e.g. in Docker)
load_dotenv()

# # Qdrant Configuration (commented out - switched to ChromaDB)
# QDRANT_HOST: str = os.getenv("QDRANT_HOST", "qdrant")
# QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", "6333"))

# ChromaDB Configuration
CHROMA_PERSIST_DIR: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma_data")

# ElevenLabs Configuration
ELEVENLABS_API_KEY: Optional[str] = os.getenv("ELEVENLABS_API_KEY")

# Groq Configuration
GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Vector Database Collection Name
COLLECTION_NAME: str = "medical_knowledge"

# Vector Embedding Model
EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

# API Configuration
API_HOST: str = "0.0.0.0"
API_PORT: int = 8000

# Paths
PROJECT_ROOT: str = os.path.dirname(os.path.abspath(__file__))
DATA_DIR: str = os.path.join(PROJECT_ROOT, "data")
DISEASES_FILE: str = os.path.join(DATA_DIR, "diseases.json")
