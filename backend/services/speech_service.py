"""
Speech-to-text service for converting audio to text using ElevenLabs API.
"""
import os
from typing import Optional
import requests
import config


class SpeechService:
    """Service for converting speech audio to text."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the speech service.
        
        Args:
            api_key: ElevenLabs API key. Defaults to environment variable.
        """
        self.api_key = api_key or config.ELEVENLABS_API_KEY
        self.api_base_url = "https://api.elevenlabs.io/v1"
    
    def speech_to_text(self, audio_file_path: str) -> str:
        """
        Convert audio file to text using ElevenLabs API.
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            Transcribed text
            
        Raises:
            FileNotFoundError: If audio file not found
            ValueError: If API key not configured
            RuntimeError: If API request fails
        """
        if not self.api_key:
            raise ValueError(
                "ElevenLabs API key not configured. "
                "Set ELEVENLABS_API_KEY environment variable."
            )
        
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
        
        try:
            # Open audio file
            with open(audio_file_path, 'rb') as audio_file:
                files = {'audio': audio_file}
                headers = {
                    'xi-api-key': self.api_key
                }
                
                # Call ElevenLabs speech-to-text API
                response = requests.post(
                    f"{self.api_base_url}/speech-to-text",
                    files=files,
                    headers=headers,
                    timeout=30
                )
                
                response.raise_for_status()
                
                result = response.json()
                transcription = result.get('transcription', '')
                
                if not transcription:
                    raise RuntimeError("No transcription received from API")
                
                return transcription
        
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"API request failed: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Failed to transcribe audio: {str(e)}")
    
    def speech_to_text_from_bytes(self, audio_bytes: bytes, filename: str = "audio.mp3") -> str:
        """
        Convert audio bytes to text using ElevenLabs API.
        
        Args:
            audio_bytes: Audio data as bytes
            filename: Filename hint for the audio file
            
        Returns:
            Transcribed text
            
        Raises:
            ValueError: If API key not configured
            RuntimeError: If API request fails
        """
        if not self.api_key:
            raise ValueError(
                "ElevenLabs API key not configured. "
                "Set ELEVENLABS_API_KEY environment variable."
            )
        
        try:
            files = {'audio': (filename, audio_bytes)}
            headers = {
                'xi-api-key': self.api_key
            }
            
            # Call ElevenLabs speech-to-text API
            response = requests.post(
                f"{self.api_base_url}/speech-to-text",
                files=files,
                headers=headers,
                timeout=30
            )
            
            response.raise_for_status()
            
            result = response.json()
            transcription = result.get('transcription', '')
            
            if not transcription:
                raise RuntimeError("No transcription received from API")
            
            return transcription
        
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"API request failed: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Failed to transcribe audio: {str(e)}")
    
    def is_api_configured(self) -> bool:
        """Check if ElevenLabs API is properly configured."""
        return bool(self.api_key)


# Global speech service instance
_speech_service: Optional[SpeechService] = None


def get_speech_service() -> SpeechService:
    """Get or create the global speech service instance."""
    global _speech_service
    if _speech_service is None:
        _speech_service = SpeechService()
    return _speech_service
