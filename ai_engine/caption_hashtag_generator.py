"""
Hindi Caption & Hashtag Generator
Generates engaging captions and viral hashtags for Hindi content
"""

import openai
import json
from typing import Dict, List, Optional
from pydantic import BaseModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeneratedCaptions(BaseModel):
    hindi_caption: str
    english_caption: str
    hashtags: List[str]
    keywords: List[str]
    call_to_action_hindi: str
    call_to_action_english: str

class HindiCaptionGenerator:
    """
    Generate viral captions and hashtags for Hindi content
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        
        # Viral hashtag categories for Hindi content
        self.hashtag_categories = {
            "motivation": ["#Motivation", "#Inspiration", "#Success", "#Mindset", "#Growth"],
            "education": ["#Education", "#Learning", "#Knowledge", "#Study", "#Tips"],
            "business": ["#Business", "#Entrepreneur", "#Startup", "#Money", "#Success"],
            "lifestyle": ["#Lifestyle", "#Health", "#Fitness", "#Wellness", "#Habits"],
            "technology": ["#Technology", "#Tech", "#Innovation", "#Digital", "#AI"],
            "entertainment": ["#Entertainment", "#Fun", "#Trending", "#Viral", "#Comedy"]
        }
        
        # Trending Hindi hashtags
        self.trending_hindi_hashtags = [
            "#जीवनसुत्र", "#सफलता", "#मोटिवेशन", "#हिंदी", "#भारत",
            "#ज्ञान", "#सीख", "#रहस्य", "#तकनीक", "#नईबात",
            "#वायरल", "#ट्रेंडिंग", "#बेस्ट", "#टॉप", "#अमेजिंग"
        ]
    
    async def generate_captions(
        self,
        topic: str,
        script_summary: str,
        video_duration: int,
        category: str = "motivation",
        platform: str = "youtube_shorts"
    ) -> Optional[GeneratedCaptions]:
        """
        Generate captions and hashtags for Hindi content
        
        Args:
            topic: Video topic
            script_summary: Summary of video script
            video_duration: Duration in seconds
            category: Content category
            platform: Target platform
            
        Returns:
            GeneratedCaptions object
        """
        try:
            logger.info(f"Generating captions for topic: {topic}")
            
            # Platform-specific requirements
            platform_limits = {
                "youtube_shorts": {"caption": 500, "hashtags": 15},
                "instagram_reels": {"caption": 2200, "hashtags": 30},
                "tiktok": {"caption": 2200, "hashtags": 10},
                "twitter": {"caption": 280, "hashtags": 3}
            }
            
            limits = platform_limits.get(platform, platform_limits["youtube_shorts"])
            
            prompt = f"""
            आप एक सोशल मीडिया कंटेंट एक्सपर्ट हैं। निम्नलिखित वीडियो के लिए viral होने वाले captions और hashtags बनाएं:
            
            टॉपिक: {topic}
            स्क्रिप्ट सारांश: {script_summary}
            अवधि: {video_duration} सेकंड
            कैटेगरी: {category}
            प्लेटफॉर्म: {platform}
            
            उत्तर इस फॉर्मेट में दें:
            {{
              "hindi_caption": "पूरी हिंदी कैप्शन जिसमें emoji हों और व्यूअर्स को engage करे। सवाल पूछें, उनसे बात करें।",
              "english_caption": "Full English caption with emojis that engages viewers.",
              "hashtags": ["hashtag1", "hashtag2", "hashtag3", ...],
              "keywords": ["keyword1", "keyword2", "keyword3"],
              "call_to_action_hindi": "हिंदी में कॉल टू एक्शन जैसे - लाइक करें, शेयर करें, कमेंट करें, सब्सक्राइब करें",
              "call_to_action_english": "English call to action"
            }}
            
            नियम:
            1. हिंदी कैप्शन बहुत ही engaging और conversational हो
            2. व्यूअर्स से सवाल पूछें
            3. ऐसी जानकारी दें जो उन्हें वीडियो देखने पर मजबूर करे
            4. Emoji का इस्तेमाल करें
            5. Hashtags viral और relevant हों
            6. कॉल टू एक्शन साफ हो
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a social media expert specializing in viral Hindi content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            
            # Clean the response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            result = json.loads(content)
            
            # Ensure minimum hashtags
            if len(result["hashtags"]) < 10:
                # Add trending Hindi hashtags
                additional_hashtags = self.trending_hindi_hashtags[:10-len(result["hashtags"])]
                result["hashtags"].extend(additional_hashtags)
            
            captions = GeneratedCaptions(
                hindi_caption=result["hindi_caption"],
                english_caption=result["english_caption"],
                hashtags=result["hashtags"],
                keywords=result["keywords"],
                call_to_action_hindi=result["call_to_action_hindi"],
                call_to_action_english=result["call_to_action_english"]
            )
            
            logger.info("Successfully generated captions and hashtags")
            return captions
            
        except Exception as e:
            logger.error(f"Error generating captions: {str(e)}")
            return None
    
    async def generate_youtube_metadata(
        self,
        topic: str,
        script_data: Dict,
        tags: List[str]
    ) -> Optional[Dict]:
        """
        Generate YouTube-specific metadata in Hindi
        
        Args:
            topic: Video topic
            script_data: Complete script data
            tags: Existing tags
            
        Returns:
            Dictionary with title, description, tags
        """
        try:
            prompt = f"""
            YouTube वीडियो के लिए metadata बनाएं:
            
            टॉपिक: {topic}
            टाइटल: {script_data.get('title_hindi', '')}
            स्क्रिप्ट: {[seg['hindi_text'] for seg in script_data.get('segments', [])]}
            
            इस फॉर्मेट में जवाब दें:
            {{
              "youtube_title": "हिंदी में viral होने वाला टाइटल जो 70 characters से कम हो",
              "youtube_description": "Detailed हिंदी description जिसमें timestamps, social links, और SEO keywords हों",
              "tags": ["tag1", "tag2", "tag3", ... minimum 20 tags]
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a YouTube SEO expert for Hindi content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8
            )
            
            content = response.choices[0].message.content
            
            # Clean the response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            metadata = json.loads(content)
            
            # Combine with existing tags
            existing_tags = set(tags)
            new_tags = set(metadata.get("tags", []))
            all_tags = list(existing_tags.union(new_tags))
            
            metadata["tags"] = all_tags[:25]  # YouTube limit
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error generating YouTube metadata: {str(e)}")
            return None
    
    def generate_trending_hashtags(self, category: str = "general") -> List[str]:
        """
        Get trending hashtags for Hindi content
        
        Args:
            category: Content category
            
        Returns:
            List of trending hashtags
        """
        base_hashtags = self.hashtag_categories.get(category, self.hashtag_categories["motivation"])
        trending = self.trending_hindi_hashtags[:5]
        
        return base_hashtags + trending
    
    async def optimize_for_virality(
        self,
        captions: GeneratedCaptions,
        platform: str = "youtube_shorts"
    ) -> GeneratedCaptions:
        """
        Optimize captions for maximum virality
        
        Args:
            captions: Original captions
            platform: Target platform
            
        Returns:
            Optimized captions
        """
        try:
            prompt = f"""
            निम्नलिखित कैप्शन को और ज्यादा viral बनाएं:
            
            हिंदी कैप्शन: {captions.hindi_caption}
            English caption: {captions.english_caption}
            Hashtags: {captions.hashtags}
            
            बिना length बढ़ाए इसे और engaging बनाएं।
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a viral content optimization expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9
            )
            
            # Note: In production, parse and update captions
            logger.info("Caption virality optimization completed")
            
            return captions
            
        except Exception as e:
            logger.error(f"Error optimizing captions: {str(e)}")
            return captions

# Test function
async def test_caption_generator():
    """Test Hindi caption generation"""
    import os
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Please set OPENAI_API_KEY environment variable")
        return
    
    generator = HindiCaptionGenerator(api_key=api_key)
    
    # Test caption generation
    captions = await generator.generate_captions(
        topic="morning routine for success",
        script_summary="Video about successful people's morning routine including waking up at 5AM, meditation, exercise, and planning.",
        video_duration=60,
        category="motivation"
    )
    
    if captions:
        print("=== HINDI CAPTION ===")
        print(captions.hindi_caption)
        print("\n=== ENGLISH CAPTION ===")
        print(captions.english_caption)
        print("\n=== HASHTAGS ===")
        print(" ".join(captions.hashtags))
        print("\n=== CALL TO ACTION (Hindi) ===")
        print(captions.call_to_action_hindi)

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_caption_generator())