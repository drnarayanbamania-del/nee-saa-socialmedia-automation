"""
Hindi Content Image Generator
Generates cinematic images for Hindi video scripts
"""

import openai
import os
import requests
from typing import Optional, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HindiImageGenerator:
    """
    Generate cinematic images optimized for Hindi content
    """
    
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        
        # Image generation parameters optimized for Hindi content
        self.image_styles = {
            "cinematic": "cinematic, dramatic lighting, professional photography, 8k",
            "animated": "animated, vibrant colors, digital art, modern style",
            "realistic": "photorealistic, natural lighting, high detail",
            "minimalist": "minimalist, clean design, modern aesthetic",
            "bollywood": "bollywood style, dramatic, colorful, indian aesthetic"
        }
        
        self.aspect_ratios = {
            "youtube_shorts": "9:16",
            "instagram_reels": "9:16", 
            "tiktok": "9:16",
            "youtube_video": "16:9"
        }
    
    def generate_scene_image(
        self, 
        visual_prompt: str,
        hindi_text: str,
        scene_number: int,
        style: str = "cinematic",
        platform: str = "youtube_shorts"
    ) -> Optional[str]:
        """
        Generate image for a specific scene
        
        Args:
            visual_prompt: Description of the visual
            hindi_text: Hindi text to be shown on scene
            scene_number: Scene number for filename
            style: Image style (cinematic, animated, etc.)
            platform: Target platform for aspect ratio
            
        Returns:
            Path to generated image or None if failed
        """
        try:
            logger.info(f"Generating image for scene {scene_number}: {visual_prompt[:50]}...")
            
            # Enhance prompt for Hindi content
            style_prompt = self.image_styles.get(style, self.image_styles["cinematic"])
            
            # Add cultural context for Hindi content
            cultural_context = "Indian setting, relatable to Indian audience"
            
            # Construct final prompt
            enhanced_prompt = f"""
            {visual_prompt}
            
            Style: {style_prompt}
            Setting: {cultural_context}
            Text overlay: {hindi_text}
            High quality, professional, engaging
            """.strip()
            
            # Generate image using DALL-E 3
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=enhanced_prompt,
                size="1024x1792" if platform in ["youtube_shorts", "instagram_reels", "tiktok"] else "1792x1024",
                quality="standard",
                n=1
            )
            
            # Get image URL
            image_url = response.data[0].url
            
            # Download and save image
            output_dir = "generated_images"
            os.makedirs(output_dir, exist_ok=True)
            
            output_path = os.path.join(output_dir, f"scene_{scene_number:02d}.png")
            
            # Download image
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                f.write(image_response.content)
            
            logger.info(f"Image saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating image for scene {scene_number}: {str(e)}")
            return None
    
    def generate_script_images(
        self, 
        script_segments: List[dict],
        style: str = "cinematic",
        platform: str = "youtube_shorts"
    ) -> List[dict]:
        """
        Generate images for all script segments
        
        Args:
            script_segments: List of script segments with visual_prompt and hindi_text
            style: Image style to use
            platform: Target platform
            
        Returns:
            List of generated image paths
        """
        try:
            generated_images = []
            
            for i, segment in enumerate(script_segments):
                visual_prompt = segment.get("visual_prompt", "")
                hindi_text = segment.get("hindi_text", "")
                
                if not visual_prompt:
                    # Generate visual prompt from hindi text if not provided
                    visual_prompt = f"Visual representation of: {hindi_text}"
                
                image_path = self.generate_scene_image(
                    visual_prompt=visual_prompt,
                    hindi_text=hindi_text,
                    scene_number=i + 1,
                    style=style,
                    platform=platform
                )
                
                if image_path:
                    generated_images.append({
                        "scene_number": i + 1,
                        "image_path": image_path,
                        "hindi_text": hindi_text,
                        "visual_prompt": visual_prompt
                    })
            
            logger.info(f"Generated {len(generated_images)} images for script")
            return generated_images
            
        except Exception as e:
            logger.error(f"Error generating script images: {str(e)}")
            return []
    
    def generate_thumbnail(
        self,
        topic: str,
        hindi_title: str,
        style: str = "bollywood",
        platform: str = "youtube_shorts"
    ) -> Optional[str]:
        """
        Generate viral thumbnail for Hindi content
        
        Args:
            topic: Video topic
            hindi_title: Hindi title text
            style: Thumbnail style
            platform: Target platform
            
        Returns:
            Path to generated thumbnail
        """
        try:
            logger.info(f"Generating thumbnail for: {hindi_title}")
            
            style_prompt = self.image_styles.get(style, self.image_styles["bollywood"])
            
            # Create viral thumbnail prompt
            thumbnail_prompt = f"""
            Viral YouTube thumbnail for topic: {topic}
            Bold Hindi text: "{hindi_title}"
            Style: {style_prompt}
            Elements: shocked expression, bright colors, bold text, clickbait style
            Indian audience appeal, high contrast, professional
            Text should be clearly visible and attention grabbing
            """
            
            # Generate thumbnail
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=thumbnail_prompt.strip(),
                size="1024x1024",
                quality="standard",
                n=1
            )
            
            # Download and save thumbnail
            image_url = response.data[0].url
            
            output_dir = "thumbnails"
            os.makedirs(output_dir, exist_ok=True)
            
            output_path = os.path.join(output_dir, f"thumbnail_{hindi_title[:20].replace(' ', '_')}.png")
            
            # Download image
            import requests
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                f.write(image_response.content)
            
            logger.info(f"Thumbnail saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating thumbnail: {str(e)}")
            return None

# Test function
def test_image_generator():
    """Test Hindi image generation"""
    import os
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Please set OPENAI_API_KEY environment variable")
        return
    
    generator = HindiImageGenerator(api_key=api_key)
    
    # Test scene image
    visual_prompt = "A person waking up early morning at 5AM, stretching, sun rising"
    hindi_text = "सुबह 5 बजे उठें"
    
    image_path = generator.generate_scene_image(
        visual_prompt=visual_prompt,
        hindi_text=hindi_text,
        scene_number=1
    )
    
    print(f"Generated image: {image_path}")

if __name__ == "__main__":
    test_image_generator()