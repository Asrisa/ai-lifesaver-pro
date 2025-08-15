# tools/tts.py - Fixed version
import os
import re
from openai import OpenAI

_client = None

def _client_once():
    global _client
    if _client is None:
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OPENAI_API_KEY not set in environment variables")
        _client = OpenAI(api_key=key)
    return _client

def clean_text_for_tts(text: str) -> str:
    """Clean text for better TTS pronunciation"""
    # Remove markdown formatting
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Remove **bold**
    text = re.sub(r'\*(.*?)\*', r'\1', text)      # Remove *italic*
    text = re.sub(r'#{1,6}\s*', '', text)         # Remove headers
    text = re.sub(r'[•▪▫‣⁃]', ' ', text)          # Convert bullets to spaces
    text = re.sub(r'\n+', '. ', text)             # Replace newlines with periods
    text = re.sub(r'\s+', ' ', text)              # Normalize whitespace
    
    # Replace symbols and emojis for better pronunciation
    replacements = {
        '🚨': 'Alert: ',
        '🏥': 'Medical: ',
        '📞': 'Contact: ',
        '⚠️': 'Warning: ',
        '🔍': 'Analysis: ',
        '👁️': 'Watch for: ',
        '🚫': 'Do not: ',
        '⏱️': 'Time: ',
        '🩹': 'Self-care: ',
        '🌡️': 'Weather: ',
        '📍': 'Location: ',
        '🗺️': 'Maps: ',
        '💡': 'Note: ',
        '⚕️': 'Medical: ',
        'N/A': 'not available',
        '★': ' stars',
        '%': ' percent',
        'Dr.': 'Doctor',
        'St.': 'Street',
        'Ave.': 'Avenue',
        'Rd.': 'Road',
        'vs.': 'versus',
        'etc.': 'etcetera',
        '°C': ' degrees Celsius',
        '°F': ' degrees Fahrenheit'
    }
    
    for symbol, replacement in replacements.items():
        text = text.replace(symbol, replacement)
    
    # Remove URLs and markdown links
    text = re.sub(r'https?://[^\s]+', 'web link', text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    return text.strip()

def tts_to_mp3_bytes(text: str, voice: str = "alloy") -> bytes:
    """Convert text to MP3 bytes using OpenAI TTS"""
    client = _client_once()
    
    # Clean and prepare text
    clean_text = clean_text_for_tts(text)
    
    # OpenAI TTS has a 4096 character limit
    if len(clean_text) > 4000:
        clean_text = clean_text[:4000] + "... Assessment truncated for audio."
    
    if not clean_text.strip():
        raise ValueError("No text content to convert to speech")
    
    try:
        # Use the correct model name for OpenAI TTS
        resp = client.audio.speech.create(
            model="tts-1",  # ✅ Correct model name (was "gpt-4o-mini-tts")
            voice=voice,    # alloy, echo, fable, onyx, nova, shimmer
            input=clean_text,
            response_format="mp3"
        )
        
        # Return the audio content
        return resp.content
        
    except Exception as e:
        raise RuntimeError(f"TTS generation failed: {str(e)}")

def test_tts():
    """Test TTS functionality"""
    try:
        test_text = "Testing text to speech functionality. This is a medical assessment system."
        audio_bytes = tts_to_mp3_bytes(test_text)
        print(f"✅ TTS test successful! Generated {len(audio_bytes)} bytes of audio.")
        return True
    except Exception as e:
        print(f"❌ TTS test failed: {e}")
        return False

if __name__ == "__main__":
    # Test the TTS functionality
    test_tts()
