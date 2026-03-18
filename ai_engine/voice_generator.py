"""
Hindi Voice Generator Module
Converts Hindi text to realistic speech using advanced TTS.
Primary provider: Edge TTS
Fallback provider: Sarvam AI
"""

import os
import tempfile
from typing import Optional, Dict, Any
import edge_tts
import asyncio
from pydub import AudioSegment
import logging
import requests
import base64
from io import BytesIO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HindiVoiceGenerator:
    """
    Generate realistic Hindi voiceovers using a resilient fallback chain.
    Primary: edge-tts
    Fallback: Sarvam AI
    Last resort: generated silent audio so video composition can still succeed
    """
    
    def __init__(self):
        # Hindi voice options - male and female
        self.hindi_voices = {
            "female_neutral": "hi-IN-SwaraNeural",
            "female_friendly": "hi-IN-SwaraNeural",
            "male_neutral": "hi-IN-MadhurNeural",
            "male_deep": "hi-IN-MadhurNeural",
            "cinematic": "hi-IN-MadhurNeural",
            "neutral": "hi-IN-SwaraNeural"
        }
        
        # Voice styles for different content types
        self.voice_styles = {
            "entertaining": "cheerful",
            "educational": "formal",
            "business": "professional",
            "emotional": "empathetic",
            "motivational": "inspirational"
        }

        # Fallback providers
        self.primary_provider = os.getenv("VOICE_PROVIDER_PRIMARY", "edge_tts")
        self.fallback_provider = os.getenv("VOICE_PROVIDER_FALLBACK", "sarvam")
        self.sarvam_api_key = os.getenv("SARVAM_API_KEY")
        self.sarvam_tts_url = os.getenv("SARVAM_TTS_URL", "https://api.sarvam.ai/text-to-speech")
    
    async def generate_voiceover(
        self, 
        hindi_text: str,
        output_path: str,
        voice_type: str = "female_neutral",
        style: str = "entertaining",
        rate: str = "+10%",
        volume: str = "+0%"
    ) -> Optional[str]:
        """
        Generate Hindi voiceover from text with fallback support.
        Order:
        1. Edge TTS
        2. Sarvam AI
        3. Local silent fallback
        """
        logger.info(f"Generating Hindi voiceover for text: {hindi_text[:50]}...")

        providers = [self.primary_provider, self.fallback_provider, "silent"]
        attempted = []

        for provider in providers:
            if provider in attempted:
                continue
            attempted.append(provider)

            try:
                if provider == "edge_tts":
                    result = await self._generate_with_edge_tts(
                        hindi_text=hindi_text,
                        output_path=output_path,
                        voice_type=voice_type,
                        rate=rate,
                        volume=volume
                    )
                elif provider == "sarvam":
                    result = await self._generate_with_sarvam(
                        hindi_text=hindi_text,
                        output_path=output_path,
                        voice_type=voice_type,
                        style=style
                    )
                else:
                    result = self._generate_silent_fallback(
                        output_path=output_path,
                        text=hindi_text
                    )

                if result:
                    logger.info(f"Voiceover saved to {output_path} using {provider}")
                    return result
            except Exception as e:
                logger.warning(f"Voice provider {provider} failed: {str(e)}")

        logger.error("All voice generation providers failed")
        return None

    async def _generate_with_edge_tts(
        self,
        hindi_text: str,
        output_path: str,
        voice_type: str,
        rate: str,
        volume: str
    ) -> Optional[str]:
        voice = self.hindi_voices.get(voice_type, "hi-IN-SwaraNeural")
        communicate = edge_tts.Communicate(hindi_text, voice, rate=rate, volume=volume)
        await communicate.save(output_path)
        return output_path

    async def _generate_with_sarvam(
        self,
        hindi_text: str,
        output_path: str,
        voice_type: str,
        style: str
    ) -> Optional[str]:
        if not self.sarvam_api_key:
            logger.warning("SARVAM_API_KEY not configured, skipping Sarvam fallback")
            return None

        payload: Dict[str, Any] = {
            "text": hindi_text,
            "target_language_code": "hi-IN",
            "speaker": "meera" if "female" in voice_type else "anush",
            "pace": 1.0,
            "loudness": 1.0,
            "speech_sample_rate": 22050,
            "enable_preprocessing": True
        }

        headers = {
            "Content-Type": "application/json",
            "api-subscription-key": self.sarvam_api_key
        }

        response = requests.post(self.sarvam_tts_url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        data = response.json()

        audio_b64 = data.get("audios", [None])[0] or data.get("audio")
        if not audio_b64:
            logger.warning("Sarvam response did not include audio payload")
            return None

        audio_bytes = base64.b64decode(audio_b64)
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
        return output_path

    def _generate_silent_fallback(self, output_path: str, text: str = "") -> Optional[str]:
        """Create a short silent mp3 fallback based on text length so video generation never blocks."""
        try:
            word_count = max(1, len(text.split()))
            duration_ms = max(2000, min(15000, word_count * 380))
            silent = AudioSegment.silent(duration=duration_ms)
            silent.export(output_path, format="mp3")
            return output_path
        except Exception as e:
            logger.error(f"Silent fallback generation failed: {str(e)}")
            return None

    def generate_scene_voice(
        self,
        text: str,
        scene_number: int,
        voice_type: str = "cinematic",
        output_dir: str = "temp"
    ) -> Dict[str, Any]:
        """
        Synchronous wrapper expected by the coordinator/workflow engine.
        Returns audio bytes and metadata.
        """
        try:
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"scene_voice_{scene_number:02d}.mp3")

            generated_path = asyncio.run(
                self.generate_voiceover(
                    hindi_text=text,
                    output_path=output_path,
                    voice_type=voice_type if voice_type in self.hindi_voices else "cinematic",
                    style="entertaining"
                )
            )

            if not generated_path or not os.path.exists(generated_path):
                return {"success": False, "error": "Voice generation failed"}

            with open(generated_path, "rb") as f:
                audio_data = f.read()

            return {
                "success": True,
                "audio_data": audio_data,
                "provider": "fallback_chain",
                "scene_number": scene_number,
                "file_path": generated_path
            }
        except Exception as e:
            logger.error(f"Error generating scene voice: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def generate_script_voiceover(
        self, 
        script_segments: list,
        output_dir: str,
        voice_type: str = "female_neutral"
    ) -> list:
        """
        Generate voiceovers for all segments in a script
        
        Args:
            script_segments: List of script segments with hindi_text
            output_dir: Directory to save audio files
            voice_type: Voice type to use
            
        Returns:
            List of audio file paths
        """
        try:
            os.makedirs(output_dir, exist_ok=True)
            audio_files = []
            
            logger.info(f"Generating voiceovers for {len(script_segments)} script segments")
            
            for i, segment in enumerate(script_segments):
                hindi_text = segment.get("hindi_text", "")
                if not hindi_text:
                    continue
                
                # Determine style based on scene number
                if i == 0:
                    style = "entertaining"  # Hook
                elif i == len(script_segments) - 1:
                    style = "motivational"  # Call to action
                else:
                    style = "educational" if "सीख" in hindi_text or "जानिए" in hindi_text else "entertaining"
                
                output_path = os.path.join(output_dir, f"scene_{i+1:02d}.mp3")
                
                audio_file = await self.generate_voiceover(
                    hindi_text=hindi_text,
                    output_path=output_path,
                    voice_type=voice_type,
                    style=style,
                    rate="+5%" if i == 0 else "+0%"  # Slightly faster for hook
                )
                
                if audio_file:
                    audio_files.append({
                        "scene_number": i + 1,
                        "file_path": audio_file,
                        "duration": segment.get("duration_seconds", 5),
                        "hindi_text": hindi_text
                    })
            
            logger.info(f"Generated {len(audio_files)} voiceover files")
            return audio_files
            
        except Exception as e:
            logger.error(f"Error generating script voiceovers: {str(e)}")
            return []
    
    async def merge_audio_files(self, audio_files: list, output_path: str) -> Optional[str]:
        """
        Merge multiple audio files into one
        
        Args:
            audio_files: List of audio file paths
            output_path: Output merged file path
            
        Returns:
            Path to merged audio file
        """
        try:
            if not audio_files:
                logger.error("No audio files to merge")
                return None
            
            logger.info(f"Merging {len(audio_files)} audio files")
            
            # Load first audio file
            combined = AudioSegment.from_mp3(audio_files[0]["file_path"])
            
            # Append remaining files
            for audio_info in audio_files[1:]:
                audio = AudioSegment.from_mp3(audio_info["file_path"])
                combined += audio
            
            # Export merged audio
            combined.export(output_path, format="mp3")
            
            logger.info(f"Merged audio saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error merging audio files: {str(e)}")
            return None
    
    def add_background_music(
        self, 
        voiceover_path: str, 
        music_path: str, 
        output_path: str,
        music_volume_reduction: int = 15
    ) -> Optional[str]:
        """
        Add background music to voiceover
        
        Args:
            voiceover_path: Path to voiceover audio
            music_path: Path to background music
            output_path: Output file path
            music_volume_reduction: dB to reduce music volume
            
        Returns:
            Path to final audio file
        """
        try:
            logger.info("Adding background music to voiceover")
            
            # Load audio files
            voiceover = AudioSegment.from_mp3(voiceover_path)
            music = AudioSegment.from_mp3(music_path)
            
            # Match music length to voiceover
            if len(music) < len(voiceover):
                # Loop music if it's shorter
                music = music * (len(voiceover) // len(music) + 1)
            
            music = music[:len(voiceover)]  # Trim to voiceover length
            
            # Reduce music volume
            music = music - music_volume_reduction
            
            # Overlay music on voiceover
            combined = voiceover.overlay(music)
            
            # Export final audio
            combined.export(output_path, format="mp3")
            
            logger.info(f"Audio with background music saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error adding background music: {str(e)}")
            return None

# Test function
async def test_voice_generator():
    """Test Hindi voice generation"""
    generator = HindiVoiceGenerator()
    
    test_texts = [
        "नमस्ते दोस्तों! आज हम जानेंगे सुपर सक्सेसफुल लोगों की मॉर्निंग रूटीन के बारे में।",
        "सबसे पहले वो सुबह 5 बजे उठते हैं और 10 मिनट मेडिटेशन करते हैं।",
        "इससे उनका दिन बहुत प्रोडक्टिव हो जाता है।",
        "तो दोस्तों, आप भी ट्राई करके देखिए!",
        "वीडियो पसंद आया तो like और subscribe जरूर करें!"
    ]
    
    output_dir = "temp_audio"
    os.makedirs(output_dir, exist_ok=True)
    
    for i, text in enumerate(test_texts):
        output_path = os.path.join(output_dir, f"test_{i+1}.mp3")
        await generator.generate_voiceover(text, output_path)
        print(f"Generated: {output_path}")

if __name__ == "__main__":
    asyncio.run(test_voice_generator())