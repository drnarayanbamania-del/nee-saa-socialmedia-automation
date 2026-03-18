"""
Hindi Video Composer
Combines images, audio, subtitles, and effects into final video
"""

import os
from typing import List, Optional, Dict
from moviepy.editor import ImageClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips
from moviepy.video.fx.all import fadein, fadeout
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HindiVideoComposer:
    """
    Compose Hindi videos with images, audio, and dynamic subtitles
    """
    
    def __init__(self):
        # Video specifications for different platforms
        self.video_specs = {
            "youtube_shorts": {"size": (1080, 1920), "fps": 30},
            "instagram_reels": {"size": (1080, 1920), "fps": 30},
            "tiktok": {"size": (1080, 1920), "fps": 30},
            "youtube_video": {"size": (1920, 1080), "fps": 30}
        }
        
        # Hindi font settings
        self.hindi_font_settings = {
            "font": "Mangal",
            "fontsize": 80,
            "color": "white",
            "stroke_color": "black",
            "stroke_width": 3,
            "align": "center"
        }
    
    def create_subtitle_clip(
        self, 
        hindi_text: str, 
        duration: float,
        video_size: tuple,
        position: str = "center"
    ) -> Optional[TextClip]:
        """
        Create a subtitle clip with Hindi text
        
        Args:
            hindi_text: Hindi text for subtitle
            duration: Duration of subtitle
            video_size: Video dimensions (width, height)
            position: Position of subtitle (center, bottom, top)
            
        Returns:
            TextClip object or None if failed
        """
        try:
            # Configure subtitle position
            if position == "center":
                pos = ("center", "center")
            elif position == "bottom":
                pos = ("center", video_size[1] - 200)
            elif position == "top":
                pos = ("center", 100)
            else:
                pos = ("center", "center")
            
            # Create text clip
            subtitle = TextClip(
                txt=hindi_text,
                fontsize=self.hindi_font_settings["fontsize"],
                color=self.hindi_font_settings["color"],
                stroke_color=self.hindi_font_settings["stroke_color"],
                stroke_width=self.hindi_font_settings["stroke_width"],
                font=self.hindi_font_settings["font"],
                size=(video_size[0] - 100, None),
                method="caption",
                align=self.hindi_font_settings["align"]
            )
            
            subtitle = subtitle.set_duration(duration)
            subtitle = subtitle.set_position(pos)
            
            # Add fade effects
            subtitle = fadein(subtitle, 0.5)
            subtitle = fadeout(subtitle, 0.5)
            
            return subtitle
            
        except Exception as e:
            logger.error(f"Error creating subtitle clip: {str(e)}")
            return None
    
    def create_scene_clip(
        self,
        image_path: str,
        audio_path: str,
        hindi_text: str,
        duration: float,
        video_specs: Dict
    ) -> Optional[CompositeVideoClip]:
        """
        Create a complete scene with image, audio, and subtitles
        
        Args:
            image_path: Path to scene image
            audio_path: Path to audio file
            hindi_text: Hindi subtitle text
            duration: Scene duration
            video_specs: Video specifications
            
        Returns:
            CompositeVideoClip object
        """
        try:
            # Load and prepare image
            image_clip = ImageClip(image_path)
            image_clip = image_clip.set_duration(duration)
            image_clip = image_clip.resize(height=video_specs["size"][1])
            
            # Center image if wider than video
            if image_clip.w > video_specs["size"][0]:
                image_clip = image_clip.set_position(lambda t: ('center', 0))
            else:
                image_clip = image_clip.set_position('center')
            
            # Load audio
            audio_clip = AudioFileClip(audio_path)
            
            # Create subtitle
            subtitle_clip = self.create_subtitle_clip(
                hindi_text=hindi_text,
                duration=duration,
                video_size=video_specs["size"],
                position="bottom"
            )
            
            # Combine elements
            if subtitle_clip:
                video_clip = CompositeVideoClip(
                    [image_clip, subtitle_clip],
                    size=video_specs["size"]
                )
            else:
                video_clip = CompositeVideoClip(
                    [image_clip],
                    size=video_specs["size"]
                )
            
            # Set audio
            video_clip = video_clip.set_audio(audio_clip)
            
            # Add fade effects
            video_clip = fadein(video_clip, 0.5)
            video_clip = fadeout(video_clip, 0.5)
            
            return video_clip
            
        except Exception as e:
            logger.error(f"Error creating scene clip: {str(e)}")
            return None
    
    def compose_video(
        self,
        scenes: List[Dict],
        output_path: str,
        platform: str = "youtube_shorts",
        add_background_music: bool = True,
        background_music_path: Optional[str] = None
    ) -> Optional[str]:
        """
        Compose complete video from scenes
        
        Args:
            scenes: List of scene dictionaries with image_path, audio_path, hindi_text, duration
            output_path: Output video path
            platform: Target platform
            add_background_music: Whether to add background music
            background_music_path: Path to background music file
            
        Returns:
            Path to final video or None if failed
        """
        try:
            logger.info(f"Composing video with {len(scenes)} scenes for {platform}")
            
            video_specs = self.video_specs.get(platform, self.video_specs["youtube_shorts"])
            
            scene_clips = []
            
            # Create clip for each scene
            for i, scene in enumerate(scenes):
                image_path = scene.get("image_path")
                audio_path = scene.get("audio_path")
                hindi_text = scene.get("hindi_text", "")
                duration = scene.get("duration", 5)
                
                if not image_path or not audio_path:
                    logger.warning(f"Skipping scene {i+1}: missing image or audio")
                    continue
                
                scene_clip = self.create_scene_clip(
                    image_path=image_path,
                    audio_path=audio_path,
                    hindi_text=hindi_text,
                    duration=duration,
                    video_specs=video_specs
                )
                
                if scene_clip:
                    scene_clips.append(scene_clip)
            
            if not scene_clips:
                logger.error("No valid scenes to compose video")
                return None
            
            # Concatenate all scenes
            final_video = concatenate_videoclips(scene_clips, method="compose")
            
            # Add background music if requested
            if add_background_music and background_music_path and os.path.exists(background_music_path):
                try:
                    from moviepy.editor import AudioFileClip
                    
                    bg_music = AudioFileClip(background_music_path)
                    bg_music = bg_music.volumex(0.2)  # Reduce volume to 20%
                    
                    if bg_music.duration < final_video.duration:
                        bg_music = bg_music.loop(duration=final_video.duration)
                    else:
                        bg_music = bg_music.subclip(0, final_video.duration)
                    
                    # Combine with existing audio
                    final_audio = final_video.audio
                    if final_audio:
                        mixed_audio = final_audio.set_audio(bg_music)
                        final_video = final_video.set_audio(mixed_audio)
                    else:
                        final_video = final_video.set_audio(bg_music)
                        
                except Exception as e:
                    logger.warning(f"Could not add background music: {str(e)}")
            
            # Write final video
            final_video.write_videofile(
                output_path,
                fps=video_specs["fps"],
                codec='libx264',
                audio_codec='aac',
                threads=4,
                preset='medium'
            )
            
            logger.info(f"Video composed successfully: {output_path}")
            
            # Clean up
            final_video.close()
            for clip in scene_clips:
                clip.close()
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error composing video: {str(e)}")
            return None
    
    def compose_video_from_script(
        self,
        script_data: Dict,
        images_dir: str,
        audio_dir: str,
        output_path: str,
        platform: str = "youtube_shorts",
        background_music_path: Optional[str] = None
    ) -> Optional[str]:
        """
        Compose video directly from script data
        
        Args:
            script_data: Script data with segments
            images_dir: Directory containing scene images
            audio_dir: Directory containing audio files
            output_path: Output video path
            platform: Target platform
            background_music_path: Background music path
            
        Returns:
            Path to final video
        """
        try:
            scenes = []
            
            for segment in script_data.get("segments", []):
                scene_number = segment.get("scene_number")
                
                scene = {
                    "image_path": os.path.join(images_dir, f"scene_{scene_number:02d}.png"),
                    "audio_path": os.path.join(audio_dir, f"scene_{scene_number:02d}.mp3"),
                    "hindi_text": segment.get("hindi_text", ""),
                    "duration": segment.get("duration_seconds", 5)
                }
                
                scenes.append(scene)
            
            return self.compose_video(
                scenes=scenes,
                output_path=output_path,
                platform=platform,
                background_music_path=background_music_path
            )
            
        except Exception as e:
            logger.error(f"Error composing video from script: {str(e)}")
            return None

# Test function
def test_video_composer():
    """Test video composition"""
    composer = HindiVideoComposer()
    
    # Mock scenes data
    scenes = [
        {
            "image_path": "generated_images/scene_01.png",
            "audio_path": "temp_audio/scene_01.mp3",
            "hindi_text": "सुबह 5 बजे उठें",
            "duration": 5
        },
        {
            "image_path": "generated_images/scene_02.png",
            "audio_path": "temp_audio/scene_02.mp3",
            "hindi_text": "10 मिनट मेडिटेशन करें",
            "duration": 5
        }
    ]
    
    output_path = "test_hindi_video.mp4"
    result = composer.compose_video(scenes, output_path)
    
    if result:
        print(f"Video created successfully: {result}")
    else:
        print("Failed to create video")

if __name__ == "__main__":
    test_video_composer()