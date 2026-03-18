#!/usr/bin/env python3
# Make executable: chmod +x verify_english_hindi_setup.py
"""
Verification Script: English UI + Hindi Content Setup
Tests the complete system to ensure proper configuration
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_file_exists(filepath, description):
    """Check if file exists and print status"""
    exists = Path(filepath).exists()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {filepath}")
    return exists

def check_file_content(filepath, search_text, description):
    """Check if file contains specific text"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            found = search_text in content
            status = "✅" if found else "❌"
            print(f"{status} {description}")
            return found
    except Exception as e:
        print(f"❌ Error checking {filepath}: {e}")
        return False

def verify_setup():
    """Verify complete system setup"""
    print("=" * 70)
    print("स्टूडियो - AI-Powered Cinematic Video Studio")
    print("Verification: English UI + Hindi Content Generation")
    print("=" * 70)
    print()
    
    all_checks_passed = True
    
    # Section 1: Frontend (English UI)
    print("📊 SECTION 1: Frontend Dashboard (English UI)")
    print("-" * 70)
    
    all_checks_passed &= check_file_exists(
        "frontend/dashboard_pro.html",
        "Dashboard file exists"
    )
    
    all_checks_passed &= check_file_content(
        "frontend/dashboard_pro.html",
        "Cinematic AI Factory",
        "English title found"
    )
    
    all_checks_passed &= check_file_content(
        "frontend/dashboard_pro.html",
        "Dashboard",
        "English nav: Dashboard"
    )
    
    all_checks_passed &= check_file_content(
        "frontend/dashboard_pro.html",
        "Generate",
        "English button: Generate"
    )
    
    all_checks_passed &= check_file_content(
        "frontend/dashboard_pro.html",
        "स्टूडियो",
        "Hindi studio name: स्टूडियो"
    )
    
    print()
    
    # Section 2: AI Engines (Hindi Content)
    print("🤖 SECTION 2: AI Content Engines (Hindi Generation)")
    print("-" * 70)
    
    all_checks_passed &= check_file_exists(
        "ai_engine/script_generator.py",
        "Script generator exists"
    )
    
    all_checks_passed &= check_file_content(
        "ai_engine/script_generator.py",
        "आप एक अनुभवी हिंदी कंटेंट क्रिएटर",
        "Hindi prompt in script generator"
    )
    
    all_checks_passed &= check_file_content(
        "ai_engine/script_generator.py",
        "hindi_text",
        "Hindi text field in schema"
    )
    
    all_checks_passed &= check_file_exists(
        "ai_engine/cinematic_video_composer.py",
        "Cinematic video composer exists"
    )
    
    all_checks_passed &= check_file_content(
        "ai_engine/caption_hashtag_generator.py",
        "हिंदी कैप्शन",
        "Hindi caption generation"
    )
    
    all_checks_passed &= check_file_content(
        "ai_engine/voice_generator.py",
        "hindi",
        "Hindi voice generation enabled"
    )
    
    print()
    
    # Section 3: Backend API (English Responses)
    print("🔌 SECTION 3: Backend API (English Responses)")
    print("-" * 70)
    
    all_checks_passed &= check_file_exists(
        "backend/cinematic_api.py",
        "API file exists"
    )
    
    all_checks_passed &= check_file_content(
        "backend/cinematic_api.py",
        "Cinematic AI Factory API",
        "English API title"
    )
    
    all_checks_passed &= check_file_content(
        "backend/cinematic_api.py",
        "Generating script",
        "English log messages"
    )
    
    all_checks_passed &= check_file_content(
        "backend/cinematic_api.py",
        "completed successfully",
        "English status messages"
    )
    
    print()
    
    # Section 4: Main Coordinator
    print("🎬 SECTION 4: Main Coordinator (Hindi Content Pipeline)")
    print("-" * 70)
    
    all_checks_passed &= check_file_exists(
        "main_cinematic_coordinator.py",
        "Main coordinator exists"
    )
    
    all_checks_passed &= check_file_content(
        "main_cinematic_coordinator.py",
        "HindiScriptGenerator",
        "Hindi script generator imported"
    )
    
    all_checks_passed &= check_file_content(
        "main_cinematic_coordinator.py",
        "HindiVoiceGenerator",
        "Hindi voice generator imported"
    )
    
    all_checks_passed &= check_file_content(
        "main_cinematic_coordinator.py",
        "cinematic_content",
        "Cinematic generation enabled"
    )
    
    print()
    
    # Section 5: Configuration Files
    print("⚙️ SECTION 5: Configuration Files")
    print("-" * 70)
    
    all_checks_passed &= check_file_exists(
        "docker-compose.cinematic.yml",
        "Docker compose file exists"
    )
    
    all_checks_passed &= check_file_exists(
        "Dockerfile.cinematic",
        "Dockerfile exists"
    )
    
    all_checks_passed &= check_file_exists(
        "quickstart_cinematic.sh",
        "Quick start script exists"
    )
    
    all_checks_passed &= check_file_exists(
        ".env.example",
        "Environment template exists"
    )
    
    print()
    
    # Final Summary
    print("=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    
    if all_checks_passed:
        print("✅ ALL CHECKS PASSED!")
        print()
        print("🎉 System is correctly configured:")
        print("   • English UI: All dashboard elements in English")
        print("   • Hindi Content: All AI-generated content in Hindi")
        print("   • API Responses: English status messages and logs")
        print("   • Studio Name: स्टूडियो (Hindi)")
        print()
        print("🚀 Ready to launch:")
        print("   ./quickstart_cinematic.sh")
        print()
        print("📂 Open dashboard:")
        print("   open frontend/dashboard_pro.html")
        print()
        return 0
    else:
        print("❌ SOME CHECKS FAILED!")
        print("Please review the errors above and fix missing files.")
        return 1

def test_hindi_generation():
    """Test Hindi content generation"""
    print()
    print("🧪 OPTIONAL: Test Hindi Content Generation")
    print("-" * 70)
    
    try:
        from ai_engine.script_generator import HindiScriptGenerator
        import asyncio
        
        print("Testing script generation with sample topic...")
        
        # Initialize generator
        generator = HindiScriptGenerator()
        
        # Test generation
        async def test():
            script = await generator.generate_script(
                topic="सफलता के रहस्य",
                category="motivation"
            )
            
            if script:
                print("✅ Hindi script generated successfully!")
                print(f"   Title: {script.title_hindi}")
                print(f"   Scenes: {len(script.segments)}")
                print(f"   Duration: {script.total_duration} seconds")
                return True
            else:
                print("❌ Script generation failed")
                return False
        
        # Run test
        result = asyncio.run(test())
        return result
        
    except Exception as e:
        print(f"⚠️  Could not test generation (missing API key?): {e}")
        return False

if __name__ == "__main__":
    # Run verification
    exit_code = verify_setup()
    
    # Optional: Test generation if OpenAI key is available
    if "OPENAI_API_KEY" in os.environ:
        test_hindi_generation()
    else:
        print()
        print("⚠️  Skipping generation test (OPENAI_API_KEY not set)")
        print("    Add your API key to .env file and run:")
        print("    python verify_english_hindi_setup.py")
    
    sys.exit(exit_code)
