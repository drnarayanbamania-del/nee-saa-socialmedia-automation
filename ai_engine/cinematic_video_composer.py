"""
Cinematic Video Composer - Professional Grade
Creates cinematic, consistent videos with professional editing techniques
"""

import os
import numpy as np
from typing import List, Optional, Dict, Tuple
from moviepy.editor import (
    ImageClip, AudioFileClip, TextClip, CompositeVideoClip, 
    concatenate_videoclips, ColorClip, CompositeAudioClip
)
from moviepy.video.fx.all import fadein, fadeout, crossfadein, crossfadeout
from moviepy.audio.fx.all import audio_fadein, audio_fadeout
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CinematicVideoComposer:
    """
    Professional cinematic video composer with consistent styling
    """
    
    def __init__(self):
        # Cinematic video specifications
        self.video_specs = {
            "youtube_shorts": {"size": (1080, 1920), "fps": 30, "codec": "libx264"},
            "instagram_reels": {"size": (1080, 1920), "fps": 30, "codec": "libx264"},
            "tiktok": {"size": (1080, 1920), "fps": 30, "codec": "libx264"},
        }
        
        # Cinematic color grading presets
        self.color_grading_presets = {
            "cinematic_blue": {
                "contrast": 1.1,
                "brightness": 0.95,
                "saturation": 1.2,
                "temperature": -0.1,
                "tint": 0.05
            },
            "warm_gold": {
                "contrast": 1.05,
                "brightness": 1.0,
                "saturation": 1.15,
                "temperature": 0.15,
                "tint": -0.05
            },
            "dramatic": {
                "contrast": 1.3,
                "brightness": 0.9,
                "saturation": 0.9,
                "temperature": -0.05,
                "tint": 0
            }
        }
        
        # Professional Hindi typography
        self.hindi_font_settings = {
            "title": {
                "font": "Mangal",
                "fontsize": 120,
                "color": "white",
                "stroke_color": "black",
                "stroke_width": 4,
                "align": "center",
                "kerning": 2
            },
            "subtitle": {
                "font": "Mangal",
                "fontsize": 80,
                "color": "white",
                "stroke_color": "black",
                "stroke_width": 3,
                "align": "center",
                "kerning": 1
            },
            "caption": {
                "font": "Mangal",
                "fontsize": 65,
                "color": "white",
                "stroke_color": "black",
                "stroke_width": 2.5,
                "align": "center",
                "kerning": 0.5
            }
        }
        
        # Cinematic transitions
        self.transitions = {
            "fade": {"duration": 0.8, "type": "fade"},
            "crossfade": {"duration": 1.0, "type": "crossfade"},
            "dip_to_black": {"duration": 1.2, "type": "dip_black"},
            "slide": {"duration": 0.6, "type": "slide"}
        }
        
        # Professional audio settings
        self.audio_settings = {
            "voice_volume": 1.0,
            "music_volume": 0.15,
            "fade_in_duration": 1.0,
            "fade_out_duration": 1.5,
            "compressor_threshold": -20,
            "compressor_ratio": 4
        }
    
    def apply_color_grading(self, clip: ImageClip, preset: str = "cinematic_blue") -> ImageClip:
        """
        Apply professional color grading to image clip
        
        Args:
            clip: Input image clip
            preset: Color grading preset name
            
        Returns:
            Color graded clip
        """
        try:
            settings = self.color_grading_presets.get(preset, self.color_grading_presets["cinematic_blue"])
            
            # Apply color adjustments
            def color_grade(get_frame, t):
                frame = get_frame(t)
                
                # Convert to float for processing
                frame = frame.astype(np.float32) / 255.0
                
                # Apply contrast
                frame = np.clip((frame - 0.5) * settings["contrast"] + 0.5, 0, 1)
                
                # Apply brightness
                frame = np.clip(frame * settings["brightness"], 0, 1)
                
                # Apply saturation
                gray = np.mean(frame, axis=2, keepdims=True)
                frame = gray + (frame - gray) * settings["saturation"]
                
                # Apply temperature (warm/cool)
                if settings["temperature"] != 0:
                    if settings["temperature"] > 0:  # Warmer
                        frame[:, :, 0] *= (1 + settings["temperature"])  # Red
                        frame[:, :, 2] *= (1 - settings["temperature"] * 0.5)  # Blue
                    else:  # Cooler
                        frame[:, :, 0] *= (1 + settings["temperature"] * 0.5)  # Red
                        frame[:, :, 2] *= (1 - settings["temperature"])  # Blue
                
                # Apply tint
                if settings["tint"] != 0:
                    if settings["tint"] > 0:  # Magenta
                        frame[:, :, 0] *= (1 + settings["tint"])  # Red
                        frame[:, :, 1] *= (1 - settings["tint"] * 0.5)  # Green
                    else:  # Green
                        frame[:, :, 0] *= (1 + settings["tint"] * 0.5)  # Red
                        frame[:, :, 1] *= (1 - settings["tint"])  # Green
                
                # Convert back to uint8
                frame = np.clip(frame * 255, 0, 255).astype(np.uint8)
                return frame
            
            graded_clip = clip.fl(lambda gf, t: color_grade(gf, t))
            return graded_clip
            
        except Exception as e:
            logger.error(f"Error applying color grading: {str(e)}")
            return clip
    
    def create_cinematic_text_clip(
        self, 
        text: str, 
        duration: float,
        video_size: tuple,
        style: str = "subtitle",
        animation: str = "typewriter",
        position: str = "center"
    ) -> Optional[TextClip]:
        """
        Create cinematic text with professional animations
        
        Args:
            text: Hindi text for display
            duration: Duration of text clip
            video_size: Video dimensions
            style: Text style (title, subtitle, caption)
            animation: Animation type (typewriter, fade, slide_in)
            position: Text position
            
        Returns:
            Animated text clip
        """
        try:
            settings = self.hindi_font_settings.get(style, self.hindi_font_settings["subtitle"])
            
            # Create base text clip
            txt_clip = TextClip(
                txt=text,
                fontsize=settings["fontsize"],
                color=settings["color"],
                stroke_color=settings["stroke_color"],
                stroke_width=settings["stroke_width"],
                font=settings["font"],
                size=(video_size[0] - 100, None),
                method="caption",
                align=settings["align"],
                kerning=settings.get("kerning", 0)
            )
            
            # Set position
            if position == "center":
                pos = ("center", video_size[1] // 2)
            elif position == "bottom":
                pos = ("center", video_size[1] - 250)
            elif position == "top":
                pos = ("center", 150)
            elif position == "lower_third":
                pos = ("center", video_size[1] - 350)
            else:
                pos = ("center", "center")
            
            txt_clip = txt_clip.set_duration(duration)
            txt_clip = txt_clip.set_position(pos)
            
            # Apply animations
            if animation == "typewriter":
                # Simulated typewriter effect with reveal
                txt_clip = txt_clip.crossfadein(0.3)
            elif animation == "fade":
                txt_clip = fadein(txt_clip, 0.5)
                txt_clip = fadeout(txt_clip, 0.5)
            elif animation == "slide_in":
                # Slide in from bottom with fade
                txt_clip = txt_clip.set_position(
                    lambda t: ('center', video_size[1] - 250 - 50 * np.sin(t * np.pi / duration))
                ).crossfadein(0.5)
            
            return txt_clip
            
        except Exception as e:
            logger.error(f"Error creating cinematic text clip: {str(e)}")
            return None
    
    def create_cinematic_scene(
        self,
        image_path: str,
        audio_path: str,
        narration_text: str,
        scene_number: int,
        total_scenes: int,
        video_spec: dict,
        transition_config: dict = None,
        color_preset: str = "cinematic_blue"
    ) -> Optional[CompositeVideoClip]:
        """
        Create a single cinematic scene with professional effects
        
        Args:
            image_path: Path to scene image
            audio_path: Path to narration audio
            narration_text: Hindi narration text
            scene_number: Current scene number
            total_scenes: Total number of scenes
            video_spec: Video specifications
            transition_config: Transition configuration
            color_preset: Color grading preset
            
        Returns:
            Composite video clip for the scene
        """
        try:
            # Load and process image
            image_clip = ImageClip(image_path)
            
            # Apply zoom/pan effect (Ken Burns)
            image_duration = AudioFileClip(audio_path).duration
            
            # Zoom animation parameters
            zoom_start = 1.0
            zoom_end = 1.15
            
            def zoom_effect(get_frame, t):
                frame = get_frame(t)
                
                # Calculate zoom level
                zoom_level = zoom_start + (zoom_end - zoom_start) * (t / image_duration)
                
                # Calculate crop region for zoom
                h, w = frame.shape[:2]
                new_h, new_w = int(h / zoom_level), int(w / zoom_level)
                
                # Center crop
                y1 = (h - new_h) // 2
                x1 = (w - new_w) // 2
                y2 = y1 + new_h
                x2 = x1 + new_w
                
                # Crop and resize back to original
                cropped = frame[y1:y2, x1:x2]
                
                return cropped
            
            image_clip = image_clip.fl(lambda gf, t: zoom_effect(gf, t))
            
            # Apply color grading
            image_clip = self.apply_color_grading(image_clip, color_preset)
            
            # Resize to video specs
            image_clip = image_clip.resize(video_spec["size"])
            image_clip = image_clip.set_duration(image_duration)
            
            # Add subtle vignette effect
            def add_vignette(get_frame, t):
                frame = get_frame(t)
                h, w = frame.shape[:2]
                
                # Create vignette mask
                Y, X = np.ogrid[:h, :w]
                center_y, center_x = h // 2, w // 2
                distance = np.sqrt((X - center_x)**2 + (Y - center_y)**2)
                max_distance = np.sqrt(center_x**2 + center_y**2)
                
                # Vignette strength
                vignette = 1 - (distance / max_distance) * 0.15
                vignette = np.clip(vignette, 0.85, 1.0)
                
                # Apply vignette
                if len(frame.shape) == 3:
                    vignette = vignette[:, :, np.newaxis]
                
                return (frame * vignette).astype(np.uint8)
            
            image_clip = image_clip.fl(lambda gf, t: add_vignette(gf, t))
            
            # Add cinematic black bars (letterboxing for vertical)
            bar_height = int(video_spec["size"][1] * 0.08)
            top_bar = ColorClip(size=(video_spec["size"][0], bar_height), color=(0, 0, 0))
            top_bar = top_bar.set_duration(image_duration)
            top_bar = top_bar.set_position(("center", 0))
            
            bottom_bar = ColorClip(size=(video_spec["size"][0], bar_height), color=(0, 0, 0))
            bottom_bar = bottom_bar.set_duration(image_duration)
            bottom_bar = bottom_bar.set_position(("center", video_spec["size"][1] - bar_height))
            
            # Create text overlay
            text_clip = self.create_cinematic_text_clip(
                narration_text,
                image_duration,
                video_spec["size"],
                style="caption",
                animation="typewriter",
                position="lower_third"
            )
            
            # Add scene progress indicator
            progress_text = f"{scene_number}/{total_scenes}"
            progress_clip = TextClip(
                txt=progress_text,
                fontsize=40,
                color="white",
                stroke_color="black",
                stroke_width=2,
                font="Arial"
            )
            progress_clip = progress_clip.set_duration(image_duration)
            progress_clip = progress_clip.set_position((video_spec["size"][0] - 100, video_spec["size"][1] - 80))
            
            # Compose final scene
            scene_clip = CompositeVideoClip([
                image_clip,
                top_bar,
                bottom_bar,
                text_clip,
                progress_clip
            ], size=video_spec["size"])
            
            # Load and add audio
            audio_clip = AudioFileClip(audio_path)
            audio_clip = audio_fadein(audio_clip, self.audio_settings["fade_in_duration"])
            audio_clip = audio_fadeout(audio_clip, self.audio_settings["fade_out_duration"])
            
            scene_clip = scene_clip.set_audio(audio_clip)
            
            # Add scene transition
            if transition_config:
                if transition_config["type"] == "fade":
                    scene_clip = fadein(scene_clip, transition_config["duration"])
                    scene_clip = fadeout(scene_clip, transition_config["duration"])
                elif transition_config["type"] == "crossfade":
                    scene_clip = crossfadein(scene_clip, transition_config["duration"])
                    scene_clip = crossfadeout(scene_clip, transition_config["duration"])
            
            return scene_clip
            
        except Exception as e:
            logger.error(f"Error creating cinematic scene: {str(e)}")
            return None
    
    def compose_cinematic_video(
        self,
        script_path: str,
        output_path: str,
        platform: str = "youtube_shorts",
        music_path: Optional[str] = None,
        color_preset: str = "cinematic_blue"
    ) -> bool:
        """
        Compose complete cinematic video with professional editing
        
        Args:
            script_path: Path to script JSON file
            output_path: Output video path
            platform: Target platform
            music_path: Background music path (optional)
            color_preset: Color grading preset
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load script
            with open(script_path, 'r', encoding='utf-8') as f:
                script_data = json.load(f)
            
            logger.info(f"Composing cinematic video: {script_data['title']}")
            
            video_spec = self.video_specs[platform]
            scenes = []
            scene_count = len(script_data['scenes'])
            
            # Create output directory
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Process each scene
            for i, scene in enumerate(script_data['scenes']):
                logger.info(f"Processing scene {i+1}/{scene_count}: {scene['scene_number']}")
                
                # Scene file paths
                image_path = scene['image_path']
                audio_path = scene['voice_path']
                
                if not os.path.exists(image_path):
                    logger.error(f"Image not found: {image_path}")
                    continue
                
                if not os.path.exists(audio_path):
                    logger.error(f"Audio not found: {audio_path}")
                    continue
                
                # Determine transition (not for first scene)
                transition_config = None
                if i > 0 and i < scene_count - 1:
                    transition_config = self.transitions["crossfade"]
                elif i == scene_count - 1:
                    transition_config = self.transitions["fade"]
                
                # Create cinematic scene
                scene_clip = self.create_cinematic_scene(
                    image_path=image_path,
                    audio_path=audio_path,
                    narration_text=scene['narration'],
                    scene_number=i + 1,
                    total_scenes=scene_count,
                    video_spec=video_spec,
                    transition_config=transition_config,
                    color_preset=color_preset
                )
                
                if scene_clip:
                    scenes.append(scene_clip)
            
            if not scenes:
                logger.error("No valid scenes to compose")
                return False
            
            # Concatenate all scenes
            logger.info("Concatenating scenes...")
            final_video = concatenate_videoclips(scenes, method="compose")
            
            # Add background music if provided
            if music_path and os.path.exists(music_path):
                logger.info("Adding background music...")
                music = AudioFileClip(music_path)
                
                # Loop music if shorter than video
                if music.duration < final_video.duration:
                    music = music.loop(duration=final_video.duration)
                else:
                    music = music.subclip(0, final_video.duration)
                
                # Adjust volume and add fades
                music = music.volumex(self.audio_settings["music_volume"])
                music = audio_fadein(music, 2.0)
                music = audio_fadeout(music, 3.0)
                
                # Mix with voice audio
                if final_video.audio:
                    mixed_audio = CompositeAudioClip([final_video.audio, music])
                    final_video = final_video.set_audio(mixed_audio)
            
            # Add intro and outro sequences
            logger.info("Adding intro/outro...")
            final_video = self._add_intro_outro(final_video, script_data, video_spec)
            
            # Write final video
            logger.info("Rendering final video...")
            final_video.write_videofile(
                output_path,
                fps=video_spec["fps"],
                codec=video_spec["codec"],
                audio_codec="aac",
                preset="medium",
                threads=4,
                logger=None
            )
            
            logger.info(f"Video composition completed: {output_path}")
            
            # Cleanup
            for scene in scenes:
                scene.close()
            final_video.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Error composing cinematic video: {str(e)}")
            logger.info("Attempting fallback with standard HindiVideoComposer...")
            return self._compose_with_standard_fallback(
                script_path=script_path,
                output_path=output_path,
                platform=platform,
                background_music_path=music_path
            )

    def _compose_with_standard_fallback(
        self,
        script_path: str,
        output_path: str,
        platform: str = "youtube_shorts",
        background_music_path: Optional[str] = None
    ) -> bool:
        """Fallback video rendering using the simpler standard composer."""
        try:
            from ai_engine.video_composer import HindiVideoComposer

            with open(script_path, 'r', encoding='utf-8') as f:
                script_data = json.load(f)

            scenes_payload = []
            for scene in script_data.get("scenes", []):
                image_path = scene.get("image_path")
                audio_path = scene.get("voice_path")
                if not image_path or not audio_path:
                    continue
                if not os.path.exists(image_path) or not os.path.exists(audio_path):
                    continue

                audio_duration = 5
                try:
                    audio_duration = AudioFileClip(audio_path).duration
                except Exception:
                    pass

                scenes_payload.append({
                    "image_path": image_path,
                    "audio_path": audio_path,
                    "hindi_text": scene.get("narration", ""),
                    "duration": audio_duration
                })

            if not scenes_payload:
                logger.error("Standard fallback could not find any valid scenes")
                return False

            fallback_composer = HindiVideoComposer()
            result_path = fallback_composer.compose_video(
                scenes=scenes_payload,
                output_path=output_path,
                platform=platform,
                add_background_music=bool(background_music_path and os.path.exists(background_music_path)),
                background_music_path=background_music_path
            )
            return bool(result_path)
        except Exception as fallback_error:
            logger.error(f"Standard video fallback failed: {str(fallback_error)}")
            return False
    
    def _add_intro_outro(self, video, script_data, video_spec):
        """Add professional intro and outro sequences"""
        try:
            # Create intro (3 seconds)
            intro_duration = 3.0
            
            # Background for intro
            intro_bg = ColorClip(size=video_spec["size"], color=(15, 15, 25))
            intro_bg = intro_bg.set_duration(intro_duration)
            
            # Title text
            title_clip = self.create_cinematic_text_clip(
                script_data["title"],
                intro_duration,
                video_spec["size"],
                style="title",
                animation="fade",
                position="center"
            )
            
            # Subtitle
            subtitle_clip = TextClip(
                txt="Cinematic AI Factory",
                fontsize=50,
                color="gray",
                font="Arial"
            )
            subtitle_clip = subtitle_clip.set_duration(intro_duration)
            subtitle_clip = subtitle_clip.set_position(("center", video_spec["size"][1] // 2 + 100))
            
            # Compose intro
            intro = CompositeVideoClip([intro_bg, title_clip, subtitle_clip])
            
            # Create outro (4 seconds)
            outro_duration = 4.0
            
            # Background for outro
            outro_bg = ColorClip(size=video_spec["size"], color=(15, 15, 25))
            outro_bg = outro_bg.set_duration(outro_duration)
            
            # Outro text
            outro_text = self.create_cinematic_text_clip(
                "धन्यवाद | Thanks for Watching",
                outro_duration,
                video_spec["size"],
                style="subtitle",
                animation="fade",
                position="center"
            )
            
            # Subscribe prompt
            subscribe_text = TextClip(
                txt="Like | Share | Subscribe",
                fontsize=60,
                color="white",
                stroke_color="black",
                stroke_width=2,
                font="Arial"
            )
            subscribe_text = subscribe_text.set_duration(outro_duration)
            subscribe_text = subscribe_text.set_position(("center", video_spec["size"][1] // 2 + 100))
            
            # Compose outro
            outro = CompositeVideoClip([outro_bg, outro_text, subscribe_text])
            
            # Add fade effects
            intro = fadein(intro, 0.5)
            intro = fadeout(intro, 0.5)
            outro = fadein(outro, 0.5)
            outro = fadeout(outro, 1.0)
            
            # Combine intro, main video, and outro
            final_video = concatenate_videoclips([intro, video, outro], method="compose")
            
            return final_video
            
        except Exception as e:
            logger.error(f"Error adding intro/outro: {str(e)}")
            return video
    
    def create_thumbnail(
        self,
        image_path: str,
        title: str,
        output_path: str,
        style: str = "dramatic"
    ) -> bool:
        """
        Create cinematic thumbnail for video
        
        Args:
            image_path: Source image path
            title: Video title
            output_path: Output thumbnail path
            style: Thumbnail style
            
        Returns:
            True if successful
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Open and process image
            image = Image.open(image_path)
            
            # Resize to thumbnail size (16:9)
            thumb_size = (1280, 720)
            image = image.resize(thumb_size, Image.Resampling.LANCZOS)
            
            # Enhance contrast and saturation
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.2)
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1.3)
            
            # Create drawing context
            draw = ImageDraw.Draw(image)
            
            # Add title text with outline
            try:
                font = ImageFont.truetype("Mangal.ttf", 80)
            except:
                font = ImageFont.load_default()
            
            # Text outline
            outline_color = (0, 0, 0)
            text_color = (255, 255, 255)
            
            # Draw outline
            x, y = 50, 50
            for offset in [-2, -1, 0, 1, 2]:
                draw.text((x + offset, y), title, font=font, fill=outline_color)
                draw.text((x, y + offset), title, font=font, fill=outline_color)
            
            # Draw main text
            draw.text((x, y), title, font=font, fill=text_color)
            
            # Save thumbnail
            image.save(output_path, quality=95)
            
            logger.info(f"Thumbnail created: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating thumbnail: {str(e)}")
            return False


# Example usage and testing
if __name__ == "__main__":
    composer = CinematicVideoComposer()
    
    # Example script path
    script_path = "output/scripts/script_20241106_120000.json"
    output_path = "output/videos/cinematic_video_20241106_120000.mp4"
    music_path = "assets/music/cinematic_background.mp3"
    
    # Compose video
    success = composer.compose_cinematic_video(
        script_path=script_path,
        output_path=output_path,
        platform="youtube_shorts",
        music_path=music_path,
        color_preset="cinematic_blue"
    )
    
    if success:
        print("✅ Cinematic video created successfully!")
    else:
        print("❌ Failed to create cinematic video")