"""
Cinematic AI Content Factory - Main Coordinator
Orchestrates the complete pipeline for cinematic video generation
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_engine.script_generator import HindiScriptGenerator
from ai_engine.image_generator import HindiImageGenerator
from ai_engine.voice_generator import HindiVoiceGenerator
from ai_engine.cinematic_video_composer import CinematicVideoComposer
from ai_engine.caption_hashtag_generator import HindiCaptionHashtagGenerator
from scraper.trending_scraper import TrendingScraper
from automation.workflow_engine import WorkflowEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/cinematic_factory.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CinematicAIFactory:
    """
    Main coordinator for cinematic AI content generation
    """
    
    def __init__(self):
        self.script_generator = HindiScriptGenerator()
        self.image_generator = HindiImageGenerator()
        self.voice_generator = HindiVoiceGenerator()
        self.video_composer = CinematicVideoComposer()
        self.caption_generator = HindiCaptionHashtagGenerator()
        self.trending_scraper = TrendingScraper()
        self.workflow_engine = WorkflowEngine()
        
        # Create output directories
        self.setup_directories()
        
        # Cinematic configuration
        self.cinematic_config = {
            "color_preset": "cinematic_blue",
            "transition_type": "crossfade",
            "music_enabled": True,
            "thumbnail_enabled": True,
            "quality": "cinematic"  # cinematic, standard, fast
        }
    
    def setup_directories(self):
        """Create necessary output directories"""
        directories = [
            "output/scripts",
            "output/images",
            "output/voice",
            "output/videos",
            "output/thumbnails",
            "output/metadata",
            "logs",
            "assets/music",
            "temp"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def generate_cinematic_content(
        self,
        topic: str,
        category: str = "motivation",
        platform: str = "youtube_shorts",
        duration: int = 60
    ) -> dict:
        """
        Generate complete cinematic content from topic
        
        Args:
            topic: Video topic in Hindi
            category: Content category
            platform: Target platform
            duration: Video duration in seconds
            
        Returns:
            Dictionary with all generated content paths
        """
        logger.info(f"🎬 Starting cinematic content generation for: {topic}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result = {
            "topic": topic,
            "timestamp": timestamp,
            "status": "started",
            "outputs": {}
        }
        
        try:
            # Step 1: Generate script
            logger.info("📝 Generating cinematic script...")
            script_result = self.script_generator.generate_script(
                topic=topic,
                category=category,
                duration=duration,
                tone="cinematic"
            )
            
            if not script_result["success"]:
                raise Exception("Script generation failed")
            
            script_filename = f"script_{timestamp}.json"
            script_path = os.path.join("output/scripts", script_filename)
            
            with open(script_path, 'w', encoding='utf-8') as f:
                json.dump(script_result["script"], f, ensure_ascii=False, indent=2)
            
            result["outputs"]["script"] = script_path
            logger.info(f"✅ Script saved: {script_path}")
            
            # Step 2: Generate images for each scene
            logger.info("🎨 Generating cinematic images...")
            image_paths = []
            
            for i, scene in enumerate(script_result["script"]["scenes"]):
                logger.info(f"  Generating image for scene {i+1}/{len(script_result['script']['scenes'])}")
                
                image_prompt = scene.get("visual_prompt", scene["narration"])
                image_result = self.image_generator.generate_scene_image(
                    prompt=image_prompt,
                    scene_number=i + 1,
                    category=category
                )
                
                if image_result["success"]:
                    image_filename = f"image_{timestamp}_scene_{i+1}.png"
                    image_path = os.path.join("output/images", image_filename)
                    
                    # Save image
                    with open(image_path, 'wb') as f:
                        f.write(image_result["image_data"])
                    
                    image_paths.append(image_path)
                    script_result["script"]["scenes"][i]["image_path"] = image_path
                    logger.info(f"  ✅ Image saved: {image_path}")
                else:
                    logger.warning(f"  ⚠️ Failed to generate image for scene {i+1}")
                    # Use placeholder
                    placeholder_path = "assets/placeholder.png"
                    image_paths.append(placeholder_path)
                    script_result["script"]["scenes"][i]["image_path"] = placeholder_path
            
            result["outputs"]["images"] = image_paths
            
            # Update script with image paths
            with open(script_path, 'w', encoding='utf-8') as f:
                json.dump(script_result["script"], f, ensure_ascii=False, indent=2)
            
            # Step 3: Generate voice for each scene
            logger.info("🔊 Generating cinematic voiceovers...")
            voice_paths = []
            
            for i, scene in enumerate(script_result["script"]["scenes"]):
                logger.info(f"  Generating voice for scene {i+1}/{len(script_result['script']['scenes'])}")
                
                voice_result = self.voice_generator.generate_scene_voice(
                    text=scene["narration"],
                    scene_number=i + 1,
                    voice_type="cinematic"
                )
                
                if voice_result["success"]:
                    voice_filename = f"voice_{timestamp}_scene_{i+1}.mp3"
                    voice_path = os.path.join("output/voice", voice_filename)
                    
                    # Save voice file
                    with open(voice_path, 'wb') as f:
                        f.write(voice_result["audio_data"])
                    
                    voice_paths.append(voice_path)
                    script_result["script"]["scenes"][i]["voice_path"] = voice_path
                    logger.info(f"  ✅ Voice saved: {voice_path}")
                else:
                    logger.warning(f"  ⚠️ Failed to generate voice for scene {i+1}")
                    # Use silent audio placeholder
                    silent_path = "assets/silent.mp3"
                    voice_paths.append(silent_path)
                    script_result["script"]["scenes"][i]["voice_path"] = silent_path
            
            result["outputs"]["voice"] = voice_paths
            
            # Update script with voice paths
            with open(script_path, 'w', encoding='utf-8') as f:
                json.dump(script_result["script"], f, ensure_ascii=False, indent=2)
            
            # Step 4: Compose cinematic video
            logger.info("🎬 Composing cinematic video...")
            
            video_filename = f"cinematic_video_{timestamp}.mp4"
            video_path = os.path.join("output/videos", video_filename)
            
            # Use background music if enabled
            music_path = None
            if self.cinematic_config["music_enabled"]:
                music_files = ["assets/music/cinematic.mp3", "assets/music/epic.mp3", "assets/music/inspirational.mp3"]
                for music_file in music_files:
                    if os.path.exists(music_file):
                        music_path = music_file
                        break
            
            video_success = self.video_composer.compose_cinematic_video(
                script_path=script_path,
                output_path=video_path,
                platform=platform,
                music_path=music_path,
                color_preset=self.cinematic_config["color_preset"]
            )
            
            if not video_success:
                raise Exception("Video composition failed")
            
            result["outputs"]["video"] = video_path
            logger.info(f"✅ Cinematic video saved: {video_path}")
            
            # Step 5: Generate cinematic thumbnail
            if self.cinematic_config["thumbnail_enabled"] and image_paths:
                logger.info("🖼️ Generating cinematic thumbnail...")
                
                thumbnail_filename = f"thumbnail_{timestamp}.png"
                thumbnail_path = os.path.join("output/thumbnails", thumbnail_filename)
                
                thumbnail_success = self.video_composer.create_thumbnail(
                    image_path=image_paths[0],  # Use first scene image
                    title=script_result["script"]["title"],
                    output_path=thumbnail_path,
                    style="dramatic"
                )
                
                if thumbnail_success:
                    result["outputs"]["thumbnail"] = thumbnail_path
                    logger.info(f"✅ Thumbnail saved: {thumbnail_path}")
            
            # Step 6: Generate captions and hashtags
            logger.info("🏷️ Generating viral captions and hashtags...")
            
            caption_result = self.caption_generator.generate_viral_captions(
                title=script_result["script"]["title"],
                description=script_result["script"]["description"],
                category=category,
                platforms=[platform]
            )
            
            if caption_result["success"]:
                caption_filename = f"captions_{timestamp}.json"
                caption_path = os.path.join("output/metadata", caption_filename)
                
                with open(caption_path, 'w', encoding='utf-8') as f:
                    json.dump(caption_result, f, ensure_ascii=False, indent=2)
                
                result["outputs"]["captions"] = caption_path
                result["outputs"]["caption_data"] = caption_result
                logger.info(f"✅ Captions saved: {caption_path}")
            
            # Update final result
            result["status"] = "completed"
            result["outputs"]["metadata"] = {
                "title": script_result["script"]["title"],
                "description": script_result["script"]["description"],
                "duration": script_result["script"]["duration"],
                "scene_count": len(script_result["script"]["scenes"]),
                "category": category,
                "platform": platform
            }
            
            # Save complete result
            result_filename = f"complete_result_{timestamp}.json"
            result_path = os.path.join("output/metadata", result_filename)
            
            with open(result_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            logger.info("🎉 Cinematic content generation completed successfully!")
            logger.info(f"📁 Result saved: {result_path}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Cinematic content generation failed: {str(e)}")
            result["status"] = "failed"
            result["error"] = str(e)
            return result
    
    def batch_generate_from_trending(
        self,
        category: str = "all",
        limit: int = 5,
        platform: str = "youtube_shorts"
    ) -> List[dict]:
        """
        Generate cinematic videos from trending topics
        
        Args:
            category: Topic category
            limit: Number of videos to generate
            platform: Target platform
            
        Returns:
            List of generation results
        """
        logger.info(f"🚀 Starting batch generation from trending topics: {category}")
        
        # Scrape trending topics
        trending_topics = self.trending_scraper.scrape_trending_topics(
            sources=["youtube", "google_trends", "twitter"],
            category=category,
            max_results=limit * 2  # Get extra to account for failures
        )
        
        if not trending_topics["success"]:
            logger.error("Failed to scrape trending topics")
            return []
        
        results = []
        generated_count = 0
        
        for topic_data in trending_topics["topics"]:
            if generated_count >= limit:
                break
            
            try:
                topic = topic_data["title"]
                category = topic_data.get("category", "motivation")
                
                logger.info(f"🎬 Processing trending topic: {topic}")
                
                result = self.generate_cinematic_content(
                    topic=topic,
                    category=category,
                    platform=platform,
                    duration=60
                )
                
                results.append(result)
                
                if result["status"] == "completed":
                    generated_count += 1
                    logger.info(f"✅ Successfully generated video {generated_count}/{limit}")
                else:
                    logger.warning(f"⚠️ Failed to generate video for: {topic}")
                
            except Exception as e:
                logger.error(f"❌ Error processing topic '{topic}': {str(e)}")
                continue
        
        logger.info(f"🎉 Batch generation completed: {generated_count}/{limit} videos successful")
        return results
    
    def run_automated_workflow(self, workflow_id: str = None):
        """
        Run automated workflow with cinematic settings
        
        Args:
            workflow_id: Specific workflow ID (optional)
        """
        logger.info("🤖 Starting automated cinematic workflow...")
        
        # Load or create workflow
        if workflow_id:
            workflow = self.workflow_engine.get_workflow(workflow_id)
        else:
            # Create default cinematic workflow
            workflow = {
                "id": "cinematic_default",
                "name": "Cinematic Content Factory",
                "description": "Automated cinematic video generation",
                "trigger": "scheduled",
                "schedule": "0 */6 * * *",  # Every 6 hours
                "steps": [
                    {
                        "action": "scrape_trending",
                        "params": {
                            "sources": ["youtube", "google_trends"],
                            "category": "motivation",
                            "max_results": 10
                        }
                    },
                    {
                        "action": "generate_cinematic_content",
                        "params": {
                            "platform": "youtube_shorts",
                            "duration": 60,
                            "color_preset": "cinematic_blue"
                        }
                    },
                    {
                        "action": "publish",
                        "params": {
                            "platforms": ["youtube"],
                            "auto_publish": False
                        }
                    }
                ]
            }
        
        # Execute workflow
        self.workflow_engine.execute_workflow(workflow)
        
        logger.info("✅ Automated cinematic workflow completed")


def main():
    parser = argparse.ArgumentParser(description='Cinematic AI Content Factory')
    parser.add_argument('--mode', type=str, default='single', 
                       choices=['single', 'batch', 'workflow', 'trending'],
                       help='Generation mode')
    parser.add_argument('--topic', type=str, help='Video topic in Hindi')
    parser.add_argument('--category', type=str, default='motivation',
                       choices=['motivation', 'education', 'entertainment', 'news', 'lifestyle'],
                       help='Content category')
    parser.add_argument('--platform', type=str, default='youtube_shorts',
                       choices=['youtube_shorts', 'instagram_reels', 'tiktok'],
                       help='Target platform')
    parser.add_argument('--duration', type=int, default=60,
                       help='Video duration in seconds')
    parser.add_argument('--limit', type=int, default=5,
                       help='Number of videos for batch mode')
    
    args = parser.parse_args()
    
    # Initialize factory
    factory = CinematicAIFactory()
    
    if args.mode == 'single':
        if not args.topic:
            print("❌ Please provide a topic using --topic argument")
            return
        
        print(f"🎬 Generating cinematic video: {args.topic}")
        result = factory.generate_cinematic_content(
            topic=args.topic,
            category=args.category,
            platform=args.platform,
            duration=args.duration
        )
        
        if result["status"] == "completed":
            print("✅ Cinematic video generated successfully!")
            print(f"📁 Video: {result['outputs']['video']}")
            print(f"📁 Thumbnail: {result['outputs'].get('thumbnail', 'N/A')}")
            print(f"📁 Captions: {result['outputs']['caption_data']['captions'][args.platform]}")
            print(f"📊 Hashtags: {result['outputs']['caption_data']['hashtags']}")
        else:
            print(f"❌ Generation failed: {result.get('error', 'Unknown error')}")
    
    elif args.mode == 'batch':
        if args.topic:
            # Generate multiple videos on same topic
            topics = [f"{args.topic} - Part {i+1}" for i in range(args.limit)]
            results = []
            
            for topic in topics:
                result = factory.generate_cinematic_content(
                    topic=topic,
                    category=args.category,
                    platform=args.platform,
                    duration=args.duration
                )
                results.append(result)
            
            successful = sum(1 for r in results if r["status"] == "completed")
            print(f"✅ Batch generation completed: {successful}/{len(results)} successful")
        else:
            # Generate from trending topics
            print(f"🚀 Generating {args.limit} cinematic videos from trending topics...")
            results = factory.batch_generate_from_trending(
                category=args.category,
                limit=args.limit,
                platform=args.platform
            )
            
            successful = sum(1 for r in results if r["status"] == "completed")
            print(f"✅ Batch generation completed: {successful}/{len(results)} successful")
    
    elif args.mode == 'workflow':
        print("🤖 Running automated cinematic workflow...")
        factory.run_automated_workflow()
        print("✅ Automated workflow completed")
    
    elif args.mode == 'trending':
        print("🔥 Fetching trending topics...")
        trending = factory.trending_scraper.scrape_trending_topics(
            sources=["youtube", "google_trends", "twitter"],
            category=args.category,
            max_results=args.limit
        )
        
        if trending["success"]:
            print("📈 Trending topics:")
            for i, topic in enumerate(trending["topics"], 1):
                print(f"  {i}. {topic['title']} ({topic['category']}) - Score: {topic['score']}")
        else:
            print("❌ Failed to fetch trending topics")


if __name__ == "__main__":
    main()