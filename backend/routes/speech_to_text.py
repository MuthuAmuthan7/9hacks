"""
Speech-to-Text route using the ElevenLabs API.
"""
import requests
from fastapi import APIRouter, HTTPException, UploadFile, File

import config

router = APIRouter(prefix="/api", tags=["speech-to-text"])

ELEVENLABS_STT_URL = "https://api.elevenlabs.io/v1/speech-to-text"


@router.post(
    "/speech_to_text",
    summary="Convert speech to text",
    description="Upload an audio file and get the transcribed text using ElevenLabs STT",
)
async def speech_to_text(file: UploadFile = File(..., description="Audio file to transcribe")):
    """
    Transcribe an uploaded audio file using the ElevenLabs Speech-to-Text API.

    Returns:
        text: The transcribed text from the audio
    """
    api_key = config.ELEVENLABS_API_KEY
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="ELEVENLABS_API_KEY is not configured. Set it in your .env file.",
        )

    audio_bytes = await file.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        response = requests.post(
            ELEVENLABS_STT_URL,
            headers={"xi-api-key": api_key},
            files={"file": (file.filename or "audio.webm", audio_bytes, file.content_type or "audio/webm")},
            data={"model_id": "scribe_v1"},
            timeout=30,
        )
        response.raise_for_status()
        result = response.json()

        transcribed_text = result.get("text", "").strip()
        if not transcribed_text:
            raise HTTPException(
                status_code=422,
                detail="ElevenLabs returned an empty transcription. Try speaking more clearly.",
            )

        return {"text": transcribed_text}

    except requests.exceptions.HTTPError as e:
        detail = str(e)
        try:
            detail = e.response.json().get("detail", {}).get("message", detail)
        except Exception:
            pass
        raise HTTPException(status_code=502, detail=f"ElevenLabs API error: {detail}")
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="ElevenLabs API request timed out.")
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=502, detail="Could not connect to ElevenLabs API.")
