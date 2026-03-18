#!/usr/bin/env python3
"""
Hindi AI Automation Platform - Main Coordinator
Main entry point for running the complete AI content factory
"""

import asyncio
import logging
import json
import os
import sys
from datetime import datetime
from typing import Optional, Dict

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.trending_scraper import HindiTrendingScraper
from ai_engine.script_generator import HindiScriptGenerator, GeneratedScript
from ai_engine.image_generator import HindiImageGenerator
from ai_engine.voice_generator import HindiVoiceGenerator
from ai_engine.video_composer import HindiVideoComposer
from ai_engine.caption_hashtag_generator import HindiCaptionGenerator, GeneratedCaptions

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HindiAIContentFactory:
    """
    Main coordinator for Hindi AI content automation
    """
    
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        
        # Initialize all engines
        self.scraper = HindiTrendingScraper()
        self.script_generator = HindiScriptGenerator(api_key=openai_api_key)
        self.image_generator = HindiImageGenerator(api_key=openai_api_key)
        self.voice_generator = HindiVoiceGenerator()
        self.video_composer = HindiVideoComposer()
        self.caption_generator = HindiCaptionGenerator(api_key=openai_api_key)
        
        # Create output directories
        os.makedirs("generated_images", exist_ok=True)
        os.makedirs("temp_audio", exist_ok=True)
        os.makedirs("final_videos", exist_ok=True)
        os.makedirs("thumbnails", exist_ok=True)
        os.makedirs("outputs", exist_ok=True)
    
    async def run_full_automation(
        self,
        topic_filter: Optional[str] = None,
        platform: str = "youtube_shorts",
        image_style: str = "cinematic",
        voice_type: str = "female_neutral"
    ) -> Optional[Dict]:
        """
        Run complete automation pipeline: trending → script → images → voice → video → captions
        
        Args:
            topic_filter: Optional specific topic to use (instead of scraping trending)
            platform: Target platform (youtube_shorts, instagram_reels, tiktok)
            image_style: Image generation style
            voice_type: Voice type for narration
            
        Returns:
            Complete automation result
        """
        try:
            logger.info("🚀 Starting Full Hindi AI Content Factory Automation")
            logger.info("=" * 60)
            
            # Step 1: Get trending topic or use provided topic
            if topic_filter:
                logger.info(f"📋 Using provided topic: {topic_filter}")
                topic_data = {
                    "topic": topic_filter,
                    "hindi_topic": topic_filter,
                    "category": "general",
                    "trending_score": 100,
                    "source": "manual"
                }
            else:
                logger.info("🔍 Scraping trending topics...")
                trending_topics = self.scraper.get_top_topics(limit=5)
                
                if not trending_topics:
                    logger.error("❌ No trending topics found")
                    return None
                
                top_topic = trending_topics[0]
                topic_data = {
                    "topic": top_topic.topic,
                    "hindi_topic": top_topic.metadata.get("hindi_topic", top_topic.topic),
                    "category": top_topic.category,
                    "trending_score": top_topic.trending_score,
                    "source": top_topic.source
                }
                
                logger.info(f"📈 Selected trending topic: {topic_data['hindi_topic']} (Score: {topic_data['trending_score']})")
            
            # Step 2: Generate Hindi script
            logger.info("\n📝 Generating Hindi script...")
            script = await self.script_generator.generate_script(
                topic=topic_data["hindi_topic"],
                category=topic_data["category"]
            )
            
            if not script:
                logger.error("❌ Failed to generate script")
                return None
            
            logger.info(f"✅ Script generated successfully!")
            logger.info(f"   Title (Hindi): {script.title_hindi}")
            logger.info(f"   Title (English): {script.title_english}")
            logger.info(f"   Duration: {script.total_duration} seconds")
            logger.info(f"   Scenes: {len(script.segments)}")
            
            # Save script
            script_file = f"outputs/script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            self.script_generator.save_script(script, script_file)
            logger.info(f"💾 Script saved to: {script_file}")
            
            # Step 3: Generate images for each scene
            logger.info("\n🖼️  Generating scene images...")
            images = self.image_generator.generate_script_images(
                script_segments=[seg.dict() for seg in script.segments],
                style=image_style,
                platform=platform
            )
            
            if not images:
                logger.error("❌ Failed to generate images")
                return None
            
            logger.info(f"✅ Generated {len(images)} images")
            
            # Step 4: Generate Hindi voiceover
            logger.info("\n🔊 Generating Hindi voiceover...")
            audio_files = await self.voice_generator.generate_script_voiceover(
                script_segments=[seg.dict() for seg in script.segments],
                output_dir="temp_audio",
                voice_type=voice_type
            )
            
            if not audio_files:
                logger.error("❌ Failed to generate voiceover")
                return None
            
            logger.info(f"✅ Generated {len(audio_files)} audio segments")
            
            # Step 5: Compose final video
            logger.info("\n🎬 Composing final video...")
            
            # Create scenes list
            scenes = []
            for segment in script.segments:
                scenes.append({
                    "image_path": f"generated_images/scene_{segment.scene_number:02d}.png",
                    "audio_path": f"temp_audio/scene_{segment.scene_number:02d}.mp3",
                    "hindi_text": segment.hindi_text,
                    "duration": segment.duration_seconds
                })
            
            video_path = self.video_composer.compose_video(
                scenes=scenes,
                output_path=f"final_videos/{script.title_hindi[:30].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4",
                platform=platform
            )
            
            if not video_path:
                logger.error("❌ Failed to compose video")
                return None
            
            logger.info(f"✅ Video composed successfully: {video_path}")
            
            # Step 6: Generate captions and hashtags
            logger.info("\n🏷️  Generating captions and hashtags...")
            captions = await self.caption_generator.generate_captions(
                topic=topic_data["hindi_topic"],
                script_summary=script.description_hindi,
                video_duration=script.total_duration,
                category=topic_data["category"]
            )
            
            if not captions:
                logger.error("❌ Failed to generate captions")
                return None
            
            logger.info("✅ Captions generated successfully")
            
            # Step 7: Generate thumbnail
            logger.info("\n🖼️  Generating thumbnail...")
            thumbnail_path = self.image_generator.generate_thumbnail(
                topic=topic_data["hindi_topic"],
                hindi_title=script.title_hindi
            )
            
            if thumbnail_path:
                logger.info(f"✅ Thumbnail generated: {thumbnail_path}")
            else:
                logger.warning("⚠️  Failed to generate thumbnail")
            
            # Compile final result
            result = {
                "topic": topic_data,
                "script": script.dict(),
                "images": images,
                "audio_files": audio_files,
                "video_path": video_path,
                "captions": captions.dict(),
                "thumbnail_path": thumbnail_path,
                "metadata": {
                    "platform": platform,
                    "image_style": image_style,
                    "voice_type": voice_type,
                    "generated_at": datetime.now().isoformat()
                }
            }
            
            # Save complete result
            result_file = f"outputs/automation_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            logger.info("\n" + "=" * 60)
            logger.info("🎉 AUTOMATION COMPLETED SUCCESSFULLY!")
            logger.info("=" * 60)
            logger.info(f"📊 Results saved to: {result_file}")
            logger.info(f"🎬 Final video: {video_path}")
            logger.info(f"📝 Script: {script_file}")
            logger.info(f"🏷️  Captions: {len(captions.hashtags)} hashtags generated")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Automation failed: {str(e)}")
            return None
    
    async def generate_script_only(
        self,
        topic: str,
        category: str = "general"
    ) -> Optional[GeneratedScript]:
        """
        Generate only the script for a given topic
        
        Args:
            topic: Topic in Hindi
            category: Content category
            
        Returns:
            Generated script
        """
        try:
            logger.info(f"📝 Generating script only for: {topic}")
            
            script = await self.script_generator.generate_script(
                topic=topic,
                category=category
            )
            
            if script:
                script_file = f"outputs/script_{topic[:20].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                self.script_generator.save_script(script, script_file)
                logger.info(f"✅ Script saved to: {script_file}")
            
            return script
            
        except Exception as e:
            logger.error(f"❌ Script generation failed: {str(e)}")
            return None
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        try:
            import shutil
            
            temp_dirs = ["temp_audio", "generated_images"]
            
            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                    logger.info(f"🗑️  Cleaned up: {temp_dir}")
            
            logger.info("✅ Temporary files cleaned up")
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up files: {str(e)}")

async def main():
    """Main function to run the automation"""
    try:
        # Get OpenAI API key
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            logger.error("❌ OPENAI_API_KEY environment variable not set")
            print("\nPlease set your OpenAI API key:")
            print("export OPENAI_API_KEY='your-api-key-here'")
            return
        
        # Initialize factory
        factory = HindiAIContentFactory(openai_api_key=openai_api_key)
        
        # Parse command line arguments
        import argparse
        
        parser = argparse.ArgumentParser(description='Hindi AI Content Factory')
        parser.add_argument('--mode', type=str, choices=['full', 'script'], default='full',
                          help='Automation mode: full (complete pipeline) or script (only generate script)')
        parser.add_argument('--topic', type=str, help='Specific topic to use (optional)')
        parser.add_argument('--platform', type=str, choices=['youtube_shorts', 'instagram_reels', 'tiktok'],
                          default='youtube_shorts', help='Target platform')
        parser.add_argument('--style', type=str, choices=['cinematic', 'animated', 'realistic', 'bollywood'],
                          default='cinematic', help='Image generation style')
        parser.add_argument('--voice', type=str, choices=['female_neutral', 'male_neutral'],
                          default='female_neutral', help='Voice type')
        
        args = parser.parse_args()
        
        # Run automation based on mode
        if args.mode == 'script':
            # Generate script only
            topic = args.topic or "सुबह की रूटीन"  # Default topic
            script = await factory.generate_script_only(topic=topic)
            
            if script:
                print("\n" + "=" * 60)
                print("📝 GENERATED SCRIPT")
                print("=" * 60)
                print(f"Title (Hindi): {script.title_hindi}")
                print(f"Title (English): {script.title_english}")
                print(f"\nDescription (Hindi): {script.description_hindi}")
                print(f"\nScenes: {len(script.segments)}")
                print(f"Total Duration: {script.total_duration} seconds")
                print("\nFirst 3 Scenes:")
                for i, segment in enumerate(script.segments[:3], 1):
                    print(f"\n{i}. {segment.hindi_text}")
                    print(f"   Duration: {segment.duration_seconds}s")
                    print(f"   Visual: {segment.visual_prompt}")
        
        else:
            # Run full automation
            logger.info("Starting full automation pipeline...")
            result = await factory.run_full_automation(
                topic_filter=args.topic,
                platform=args.platform,
                image_style=args.style,
                voice_type=args.voice
            )
            
            if result:
                print("\n" + "=" * 80)
                print("🎉 AUTOMATION COMPLETED SUCCESSFULLY!")
                print("=" * 80)
                print(f"📹 Video: {result['video_path']}")
                print(f"📝 Script: {result['script']['title_hindi']}")
                print(f"🏷️  Hashtags: {len(result['captions']['hashtags'])} generated")
                print(f"📊 Results saved in outputs/ directory")
            else:
                logger.error("❌ Automation failed")
        
        # Cleanup
        factory.cleanup_temp_files()
        
    except KeyboardInterrupt:
        logger.info("\n⚠️  Automation interrupted by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())