"""
Hindi Script Generator Module
Generates engaging Hindi scripts for video content from trending topics
"""

import openai
import json
from typing import Dict, List, Optional
from pydantic import BaseModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScriptSegment(BaseModel):
    scene_number: int
    hindi_text: str
    english_translation: str
    scene_description: str
    duration_seconds: int
    visual_prompt: str

class GeneratedScript(BaseModel):
    topic: str
    title_hindi: str
    title_english: str
    description_hindi: str
    description_english: str
    tags: List[str]
    segments: List[ScriptSegment]
    total_duration: int
    category: str

class HindiScriptGenerator:
    """
    Advanced script generator optimized for Hindi content creation
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        
        self.hindi_prompt_template = """
        आप एक अनुभवी हिंदी कंटेंट क्रिएटर और स्क्रिप्ट राइटर हैं। 
        ट्रेंडिंग टॉपिक '{topic}' पर एक viral वीडियो स्क्रिप्ट तैयार करें जो निम्नलिखित विशेषताओं के साथ हो:
        
        स्क्रिप्ट की आवश्यकताएं:
        - लंबाई: 8-12 सीन, कुल अवधि 60-90 सेकंड
        - भाषा: रोजमर्रा की हिंदी (आसान शब्द, प्राकृतिक बोलचाल)
        - लहजा: मजेदार, दिलचस्प, viral होने वाला
        - शैली: YouTube Shorts/Reels के लिए अनुकूलित
        - संरचना: हुक → समस्या → समाधान → कॉल टू एक्शन
        
        प्रत्येक सीन के लिए प्रदान करें:
        1. हिंदी टेक्स्ट (प्राकृतिक, बोलचाल की भाषा)
        2. अंग्रेजी अनुवाद
        3. विजुअल डिस्क्रिप्शन
        4. अनुमानित अवधि (सेकंडों में)
        5. इमेज जनरेशन के लिए प्रॉम्प्ट
        
        टॉपिक: {topic}
        कैटेगरी: {category}
        
        फॉर्मेट में जवाब दें:
        {{
          "title_hindi": "हिंदी टाइटल",
          "title_english": "English Title", 
          "description_hindi": "हिंदी विवरण",
          "description_english": "English Description",
          "tags": ["tag1", "tag2", "tag3"],
          "segments": [
            {{
              "scene_number": 1,
              "hindi_text": "हिंदी टेक्स्ट",
              "english_translation": "English translation",
              "scene_description": "Visual description",
              "duration_seconds": 5,
              "visual_prompt": "Image generation prompt"
            }}
          ]
        }}
        """
    
    async def generate_script(
        self, 
        topic: str, 
        category: str = "general",
        tone: str = "entertaining",
        target_duration: int = 75
    ) -> Optional[GeneratedScript]:
        """
        Generate a complete Hindi script from a topic
        """
        try:
            logger.info(f"Generating Hindi script for topic: {topic}")
            
            prompt = self.hindi_prompt_template.format(
                topic=topic,
                category=category
            )
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert Hindi content creator and scriptwriter."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=3000
            )
            
            script_content = response.choices[0].message.content
            
            # Clean the response
            if "```json" in script_content:
                script_content = script_content.split("```json")[1].split("```")[0]
            elif "```" in script_content:
                script_content = script_content.split("```")[1].split("```")[0]
            
            script_data = json.loads(script_content)
            
            # Calculate total duration
            total_duration = sum(segment["duration_seconds"] for segment in script_data["segments"])
            
            script = GeneratedScript(
                topic=topic,
                title_hindi=script_data["title_hindi"],
                title_english=script_data["title_english"],
                description_hindi=script_data["description_hindi"],
                description_english=script_data["description_english"],
                tags=script_data["tags"],
                segments=[ScriptSegment(**segment) for segment in script_data["segments"]],
                total_duration=total_duration,
                category=category
            )
            
            logger.info(f"Successfully generated Hindi script with {len(script.segments)} scenes")
            return script
            
        except Exception as e:
            logger.error(f"Error generating Hindi script: {str(e)}")
            return None
    
    async def generate_business_script(self, product_info: Dict) -> Optional[GeneratedScript]:
        """
        Generate Hindi script for business/product promotion
        """
        topic = f"{product_info.get('name')} - {product_info.get('category')}"
        
        business_prompt = f"""
        प्रोडक्ट/सर्विस: {product_info.get('name')}
        कैटेगरी: {product_info.get('category')}
        टारगेट ऑडियंस: {product_info.get('target_audience')}
        यूएसपी: {product_info.get('usp', '')}
        
        इस प्रोडक्ट के लिए एक कन्वर्ट होने वाली हिंदी वीडियो स्क्रिप्ट बनाएं जो:
        - प्रोडक्ट की वैल्यू क्लियर करे
        - ऑडियंस की समस्या को टच करे
        - समाधान के तौर पर प्रोडक्ट पेश करे
        - कॉल टू एक्शन दे
        """
        
        return await self.generate_script(topic, "business")
    
    async def generate_educational_script(self, topic: str, level: str = "beginner") -> Optional[GeneratedScript]:
        """
        Generate Hindi script for educational content
        """
        educational_prompt = f"""
        टॉपिक: {topic}
        लेवल: {level}
        
        इस टॉपिक पर एक एजुकेशनल हिंदी वीडियो स्क्रिप्ट बनाएं जो:
        - कॉन्सेप्ट को सिंपल शब्दों में समझाए
        - रोजमर्रा के उदाहरण दे
        - व्यूअर्स को वैल्यू दे
        - आसानी से समझ में आए
        """
        
        return await self.generate_script(topic, "education")
    
    def save_script(self, script: GeneratedScript, filename: str):
        """
        Save script to JSON file
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(script.dict(), f, ensure_ascii=False, indent=2)
            logger.info(f"Script saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving script: {str(e)}")

# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_generator():
        generator = HindiScriptGenerator(api_key="your-openai-api-key")
        
        # Test trending topic
        script = await generator.generate_script(
            topic="morning routine for success",
            category="lifestyle"
        )
        
        if script:
            print(f"Title (Hindi): {script.title_hindi}")
            print(f"Title (English): {script.title_english}")
            print(f"Total Duration: {script.total_duration} seconds")
            print(f"\nFirst Scene:\n{script.segments[0].hindi_text}")
    
    asyncio.run(test_generator())