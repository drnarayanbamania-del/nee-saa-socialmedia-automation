#!/usr/bin/env python3
"""
स्टूडियो - AI-Powered Cinematic Video Studio
Sample Video Generator for Demo

This script creates a sample cinematic video to showcase the platform's capabilities.
"""

import os
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from ai_engine.script_generator import generate_script
from ai_engine.image_generator import generate_images_for_script
from ai_engine.voice_generator import generate_voiceover
from ai_engine.cinematic_video_composer import create_cinematic_video
from ai_engine.caption_hashtag_generator import generate_captions_and_hashtags

def create_sample_project():
    """Create a complete sample video project for demo purposes."""
    
    print("🎬 स्टूडियो - Sample Video Generator")
    print("=" * 50)
    
    # Sample trending topic in Hindi
    topic = "सफलता के लिए सुबह की आदतें"
    category = "motivation"
    
    print(f"\n🎯 Topic: {topic}")
    print(f"📂 Category: {category}")
    
    # Create demo directory
    demo_dir = Path("demo/output")
    demo_dir.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Generate Hindi script
    print("\n📝 Step 1: Generating Hindi script...")
    script = generate_script(topic, category)
    
    script_path = demo_dir / "script.json"
    with open(script_path, 'w', encoding='utf-8') as f:
        json.dump(script, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Script generated: {len(script['scenes'])} scenes")
    print(f"📝 Title: {script['metadata']['title']}")
    
    # Display sample scenes
    print("\n🎬 Sample Scenes:")
    for i, scene in enumerate(script['scenes'][:3], 1):
        print(f"   {i}. {scene['narration'][:60]}...")
    
    # Step 2: Generate images
    print("\n🖼️ Step 2: Generating cinematic images...")
    image_dir = demo_dir / "images"
    image_dir.mkdir(exist_ok=True)
    
    images = generate_images_for_script(script, str(image_dir))
    print(f"✅ Generated {len(images)} images")
    
    # Step 3: Generate Hindi voiceover
    print("\n🎤 Step 3: Generating Hindi voiceover...")
    
    # Create a shorter demo script (first 3 scenes)
    demo_script = script.copy()
    demo_script['scenes'] = demo_script['scenes'][:3]
    
    voice_dir = demo_dir / "voice"
    voice_dir.mkdir(exist_ok=True)
    
    voice_file = str(voice_dir / "narration.mp3")
    generate_voiceover(demo_script, voice_file)
    print("✅ Voiceover generated (Hindi)")
    
    # Step 4: Create cinematic video
    print("\n🎬 Step 4: Creating cinematic video...")
    
    video_config = {
        "color_grading": "cinematic_blue",
        "ken_burns": True,
        "vignette": True,
        "transitions": "crossfade",
        "subtitle_animation": "typewriter"
    }
    
    video_path = str(demo_dir / "sample_video.mp4")
    final_video = create_cinematic_video(
        demo_script,
        str(image_dir),
        voice_file,
        video_path,
        video_config
    )
    print("✅ Cinematic video created!")
    
    # Step 5: Generate captions and hashtags
    print("\n🏷️ Step 5: Generating captions and hashtags...")
    captions = generate_captions_and_hashtags(demo_script)
    
    captions_path = demo_dir / "captions.json"
    with open(captions_path, 'w', encoding='utf-8') as f:
        json.dump(captions, f, ensure_ascii=False, indent=2)
    
    print("✅ Captions and hashtags generated (Hindi)")
    print(f"📝 Caption: {captions['viral_caption'][:80]}...")
    print(f"🏷️ Hashtags: {captions['hashtags']}")
    
    # Create preview summary
    print("\n" + "=" * 50)
    print("🎉 Sample Video Generation Complete!")
    print("=" * 50)
    
    summary = {
        "topic": topic,
        "title": script['metadata']['title'],
        "duration": f"{len(demo_script['scenes']) * 5} seconds",
        "language": "Hindi",
        "scenes": len(demo_script['scenes']),
        "output_dir": str(demo_dir),
        "video_file": final_video,
        "features": [
            "Cinematic Blue color grading",
            "Ken Burns zoom/pan effects",
            "Vignette effect",
            "Crossfade transitions",
            "Hindi subtitles with typewriter animation",
            "Professional audio mixing"
        ]
    }
    
    summary_path = demo_dir / "summary.json"
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    # Print summary
    print(f"\n📊 Summary:")
    print(f"📁 Output Directory: {demo_dir}")
    print(f"🎬 Video: {final_video}")
    print(f"📝 Title: {summary['title']}")
    print(f"⏱️ Duration: {summary['duration']}")
    print(f"🗣️ Language: {summary['language']}")
    print(f"🎭 Scenes: {summary['scenes']}")
    
    print(f"\n✨ Cinematic Features:")
    for feature in summary['features']:
        print(f"   • {feature}")
    
    print(f"\n🎯 Next Steps:")
    print(f"   1. View the video: open {final_video}")
    print(f"   2. Open dashboard: open frontend/app_preview.html")
    print(f"   3. Deploy: ./quickstart_cinematic.sh")
    
    return summary

def main():
    """Main demo function."""
    try:
        # Check API keys
        if not os.getenv("OPENAI_API_KEY"):
            print("❌ Error: OPENAI_API_KEY not found in environment")
            print("Please set your API key: export OPENAI_API_KEY='sk-your-key'")
            sys.exit(1)
        
        # Generate sample
        summary = create_sample_project()
        
        # Create HTML preview
        create_html_preview(summary)
        
        print(f"\n🎬 Preview created at: demo/output/preview.html")
        print(f"🚀 Run: open demo/output/preview.html")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def create_html_preview(summary):
    """Create an HTML preview page for the generated video."""
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sample Video - स्टूडियो AI Studio</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body {{ background: #0f0f1a; color: white; }}
        .glass {{
            background: rgba(30, 30, 50, 0.7);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        .gradient-text {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
    </style>
</head>
<body class="p-8">
    <div class="max-w-6xl mx-auto">
        <div class="glass rounded-2xl p-8">
            <h1 class="text-4xl font-bold mb-2 gradient-text">स्टूडियो</h1>
            <p class="text-gray-400 mb-8">AI-Powered Cinematic Video - Sample Output</p>
            
            <!-- Video Section -->
            <div class="grid md:grid-cols-2 gap-8">
                <div>
                    <h2 class="text-2xl font-bold mb-4">{summary['title']}</h2>
                    <video controls class="w-full rounded-lg shadow-2xl">
                        <source src="sample_video.mp4" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>
                    <p class="text-sm text-gray-400 mt-2">
                        Duration: {summary['duration']} | Language: Hindi | Format: 9:16 Shorts/Reels
                    </p>
                </div>
                
                <div class="space-y-6">
                    <div>
                        <h3 class="text-xl font-semibold mb-3">📊 Video Details</h3>
                        <ul class="space-y-2 text-gray-300">
                            <li><strong>Topic:</strong> {summary['topic']}</li>
                            <li><strong>Scenes:</strong> {summary['scenes']}</li>
                            <li><strong>Language:</strong> Hindi</li>
                            <li><strong>Format:</strong> 1080x1920 (9:16)</li>
                        </ul>
                    </div>
                    
                    <div>
                        <h3 class="text-xl font-semibold mb-3">✨ Cinematic Features</h3>
                        <ul class="space-y-2 text-gray-300">
    """
    
    for feature in summary['features']:
        html_content += f"                            <li>• {feature}</li>\n"
    
    html_content += f"""                        </ul>
                    </div>
                    
                    <div>
                        <h3 class="text-xl font-semibold mb-3">🏷️ Sample Caption</h3>
                        <div class="bg-gray-800 rounded p-4">
                            <p class="text-white mb-2">दोस्तों, ये 5 आदतें बदल देंगी आपकी जिंदगी! 🔥</p>
                            <p class="text-blue-300 text-sm">#सफलता #मोटिवेशन #सुबहकीरूटीन</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Sample Scenes -->
            <div class="mt-8">
                <h3 class="text-xl font-semibold mb-4">🎬 Sample Scenes</h3>
                <div class="grid grid-cols-3 gap-4">
    """
    
    scene_images = ["scene_0.png", "scene_1.png", "scene_2.png"]
    scene_texts = [
        "नमस्ते दोस्तों! सफल लोगों की रूटीन जानना चाहते हैं?",
        "पहली आदत: सुबह 5 बजे उठें। समय का सम्मान करें।",
        "दूसरी आदत: मेडिटेशन करें। मन को शांत रखें।"
    ]
    
    for i, (img, text) in enumerate(zip(scene_images, scene_texts)):
        html_content += f"""
                    <div class="bg-gray-800 rounded p-3">
                        <img src="{img}" alt="Scene {i+1}" class="w-full rounded mb-2">
                        <p class="text-sm text-gray-300">{text[:50]}...</p>
                    </div>
        """
    
    html_content += f"""
                </div>
            </div>
            
            <!-- Responsive Action Buttons -->
            <div class="mt-8 glass-card p-6">
                <h3 class="text-lg font-semibold text-white mb-4">📱 Responsive Action Buttons</h3>
                <p class="text-gray-400 mb-6">These buttons adapt to different screen sizes:</p>
                
                <div class="flex flex-col sm:flex-row gap-3">
                    <!-- Share Button - Responsive -->
                    <button onclick="shareVideo()" 
                            class="flex-1 min-w-[120px] px-4 py-3 bg-blue-500/20 text-blue-400 border border-blue-500/30 rounded-lg font-medium hover:bg-blue-500/30 transition-all flex items-center justify-center gap-3 group">
                        <i class="fas fa-share-alt text-lg group-hover:scale-110 transition-transform"></i>
                        <span class="hidden sm:inline">Share Video</span>
                        <span class="sm:hidden">Share</span>
                    </button>
                    
                    <!-- Download Button - Responsive -->
                    <button onclick="downloadVideo()" 
                            class="flex-1 min-w-[120px] px-4 py-3 bg-green-500/20 text-green-400 border border-green-500/30 rounded-lg font-medium hover:bg-green-500/30 transition-all flex items-center justify-center gap-3 group">
                        <i class="fas fa-download text-lg group-hover:scale-110 transition-transform"></i>
                        <span class="hidden sm:inline">Download</span>
                        <span class="sm:hidden">Save</span>
                    </button>
                    
                    <!-- Delete Button - Responsive -->
                    <button onclick="deleteVideo()" 
                            class="flex-1 min-w-[120px] px-4 py-3 bg-red-500/20 text-red-400 border border-red-500/30 rounded-lg font-medium hover:bg-red-500/30 transition-all flex items-center justify-center gap-3 group">
                        <i class="fas fa-trash text-lg group-hover:scale-110 transition-transform"></i>
                        <span class="hidden sm:inline">Delete</span>
                        <span class="sm:hidden">Remove</span>
                    </button>
                </div>
                
                <div class="mt-4 p-3 bg-gray-800/50 rounded-lg">
                    <p class="text-xs text-gray-400">
                        <strong class="text-white">Responsive Behavior:</strong><br>
                        • <strong>Desktop (>640px):</strong> Full labels with icons<br>
                        • <strong>Tablet (480-640px):</strong> Icons with short text<br>
                        • <strong>Mobile (<480px):</strong> Icons with minimal text
                    </p>
                </div>
            </div>
            
            <div class="mt-8 text-center">
                <a href="../../../frontend/app_preview.html" class="inline-block px-6 py-3 bg-purple-600 rounded-lg hover:bg-purple-700 transition">
                    <i class="fas fa-arrow-left mr-2"></i>Back to Dashboard
                </a>
            </div>
        </div>
    </div>
</body>
</html>
    """
    
    preview_path = Path("demo/output/preview.html")
    with open(preview_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return str(preview_path)

if __name__ == "__main__":
    main()
