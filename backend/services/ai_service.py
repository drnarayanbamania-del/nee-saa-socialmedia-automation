import openai
import anthropic
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv
import json
import requests
from schemas import ScriptRequest, ImageRequest, VoiceRequest

load_dotenv()

class AIService:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        self.stability_api_key = os.getenv("STABILITY_API_KEY")
    
    async def generate_script(self, request: ScriptRequest) -> Dict[str, Any]:
        """Generate a script from a trending topic"""
        
        prompt = f"""
        Create a viral content script about: {request.topic}
        
        Requirements:
        - Target duration: {request.duration} seconds
        - Tone: {request.tone}
        - Platform: {request.platform}
        - Include a strong hook in the first 3 seconds
        - Create engaging storytelling
        - Add clear calls to action
        - Break into scenes with visual descriptions
        
        Format the response as JSON with:
        {{
          "title": "Engaging title",
          "hook": "First 3-second hook",
          "scenes": [
            {{
              "scene_number": 1,
              "timestamp": "0:00-0:15",
              "narration": "Voiceover text",
              "visual_description": "What should appear on screen",
              "transition": "Transition type"
            }}
          ],
          "duration_estimate": 60,
          "keywords": ["tag1", "tag2", "tag3"],
          "hashtags": ["#tag1", "#tag2", "#tag3"]
        }}
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert viral content creator. Create engaging scripts that maximize watch time and engagement."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            content = json.loads(response.choices[0].message.content)
            return {
                "success": True,
                "script": content,
                "model": "gpt-4-turbo-preview"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_image(self, request: ImageRequest) -> Dict[str, Any]:
        """Generate an image using DALL-E or Stable Diffusion"""
        
        try:
            # Try DALL-E first
            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=request.prompt,
                size=request.size or "1792x1024",
                quality="hd" if request.high_quality else "standard",
                n=1
            )
            
            image_url = response.data[0].url
            
            # Download the image
            image_response = requests.get(image_url)
            
            return {
                "success": True,
                "image_url": image_url,
                "image_data": image_response.content,
                "model": "dall-e-3"
            }
        except Exception as e:
            # Fallback to Stable Diffusion
            try:
                stability_response = requests.post(
                    "https://api.stability.ai/v2beta/stable-image/generate/sd3",
                    headers={
                        "Authorization": f"Bearer {self.stability_api_key}",
                        "Accept": "image/*"
                    },
                    files={"none": ''},
                    data={
                        "prompt": request.prompt,
                        "output_format": "png",
                    }
                )
                
                if stability_response.status_code == 200:
                    return {
                        "success": True,
                        "image_data": stability_response.content,
                        "model": "stable-diffusion-3"
                    }
            except:
                pass
            
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_voice(self, request: VoiceRequest) -> Dict[str, Any]:
        """Generate voiceover using ElevenLabs"""
        
        try:
            # Default voice settings
            voice_settings = request.voice_settings or {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            }
            
            # Default voice ID (professional male voice)
            voice_id = request.voice_id or "pNInz6obpgDQGcFmaJgB"
            
            response = requests.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                headers={
                    "Accept": "audio/mpeg",
                    "Content-Type": "application/json",
                    "xi-api-key": self.elevenlabs_api_key
                },
                json={
                    "text": request.text,
                    "model_id": "eleven_multilingual_v2",
                    "voice_settings": voice_settings
                }
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "audio_data": response.content,
                    "voice_id": voice_id,
                    "model": "eleven_multilingual_v2"
                }
            else:
                return {
                    "success": False,
                    "error": f"ElevenLabs API error: {response.text}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_thumbnail(self, video_title: str, style: str = "viral") -> Dict[str, Any]:
        """Generate a viral thumbnail for video"""
        
        prompt = f"""
        Create a viral YouTube thumbnail for: "{video_title}"
        
        Style: {style}
        Requirements:
        - High contrast and bright colors
        - Bold, readable text
        - Expressive facial expressions if people are included
        - Click-worthy composition
        - 16:9 aspect ratio
        - Professional quality
        """
        
        try:
            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1792x1024",
                quality="hd",
                n=1
            )
            
            image_url = response.data[0].url
            image_response = requests.get(image_url)
            
            return {
                "success": True,
                "thumbnail_url": image_url,
                "image_data": image_response.content
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_captions_and_hashtags(self, script_content: str, platform: str) -> Dict[str, Any]:
        """Generate optimized captions and hashtags"""
        
        prompt = f"""
        Create viral captions and hashtags for the following script on {platform}:
        
        Script: {script_content[:500]}...
        
        Requirements:
        - Platform-optimized caption
        - Maximum engagement
        - Relevant emojis
        - 15-30 hashtags
        - Call to action included
        
        Format as JSON with:
        {{
          "caption": "Optimized caption with emojis",
          "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3"],
          "keywords": ["keyword1", "keyword2"]
        }}
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a social media marketing expert. Create captions that maximize reach and engagement."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            content = json.loads(response.choices[0].message.content)
            return {
                "success": True,
                "captions": content
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def analyze_trending_topics(self, topics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze and rank trending topics"""
        
        prompt = f"""
        Analyze these trending topics and rank them by viral potential:
        
        Topics: {json.dumps(topics[:10], indent=2)}
        
        Consider:
        - Current relevance
        - Audience engagement potential
        - Content creation feasibility
        - Competition level
        - Monetization potential
        
        Return JSON with ranked topics and scores.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a viral content strategist. Analyze trends for maximum engagement potential."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                response_format={"type": "json_object"}
            )
            
            content = json.loads(response.choices[0].message.content)
            return content.get("ranked_topics", [])
        except Exception as e:
            return []
