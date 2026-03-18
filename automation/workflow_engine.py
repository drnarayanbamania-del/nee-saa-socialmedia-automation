"""
Automation Workflow Engine
Manages and executes automated content generation workflows
"""

import os
import json
import schedule
import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from pathlib import Path
import importlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowEngine:
    """
    Advanced workflow engine for automated content generation
    """
    
    def __init__(self):
        self.workflows: Dict[str, Dict] = {}
        self.active_jobs: Dict[str, Dict] = {}
        self.scheduler = schedule.Scheduler()
        self.is_running = False
        self.worker_thread = None
        
        # Create workflow directory
        Path("workflows").mkdir(exist_ok=True)
        Path("logs/workflows").mkdir(parents=True, exist_ok=True)
        
        # Load existing workflows
        self.load_workflows()
        
        # Initialize action handlers
        self.action_handlers = {
            "scrape_trending": self._handle_scrape_trending,
            "generate_script": self._handle_generate_script,
            "generate_images": self._handle_generate_images,
            "generate_voice": self._handle_generate_voice,
            "compose_video": self._handle_compose_video,
            "generate_cinematic_content": self._handle_cinematic_generation,
            "publish": self._handle_publish,
            "notify": self._handle_notify,
            "delay": self._handle_delay
        }
    
    def load_workflows(self):
        """Load workflows from disk"""
        try:
            workflow_files = Path("workflows").glob("*.json")
            for workflow_file in workflow_files:
                with open(workflow_file, 'r', encoding='utf-8') as f:
                    workflow = json.load(f)
                    self.workflows[workflow["id"]] = workflow
            
            logger.info(f"Loaded {len(self.workflows)} workflows")
        except Exception as e:
            logger.error(f"Error loading workflows: {str(e)}")
    
    def save_workflow(self, workflow: Dict):
        """Save workflow to disk"""
        try:
            workflow_path = Path("workflows") / f"{workflow['id']}.json"
            with open(workflow_path, 'w', encoding='utf-8') as f:
                json.dump(workflow, f, ensure_ascii=False, indent=2)
            
            self.workflows[workflow["id"]] = workflow
            logger.info(f"Saved workflow: {workflow['name']}")
        except Exception as e:
            logger.error(f"Error saving workflow: {str(e)}")
    
    def create_workflow(
        self,
        name: str,
        description: str,
        trigger: str,
        schedule: Optional[str] = None,
        steps: List[Dict] = None
    ) -> str:
        """
        Create a new workflow
        
        Args:
            name: Workflow name
            description: Workflow description
            trigger: Trigger type (manual, scheduled, webhook)
            schedule: Cron-style schedule string
            steps: List of workflow steps
            
        Returns:
            Workflow ID
        """
        workflow_id = f"wf_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        workflow = {
            "id": workflow_id,
            "name": name,
            "description": description,
            "trigger": trigger,
            "schedule": schedule,
            "steps": steps or [],
            "enabled": True,
            "created_at": datetime.now().isoformat(),
            "last_run": None,
            "run_count": 0,
            "success_count": 0,
            "failure_count": 0
        }
        
        self.save_workflow(workflow)
        
        # Schedule if needed
        if trigger == "scheduled" and schedule:
            self._schedule_workflow(workflow)
        
        return workflow_id
    
    def _schedule_workflow(self, workflow: Dict):
        """Schedule a workflow for automatic execution"""
        try:
            if workflow["schedule"]:
                # Parse cron-like schedule
                # For simplicity, using schedule library
                job = self.scheduler.every().day.at("10:00").do(self.execute_workflow, workflow["id"])
                self.active_jobs[workflow["id"]] = {
                    "job": job,
                    "workflow_id": workflow["id"]
                }
                
                logger.info(f"Scheduled workflow: {workflow['name']} ({workflow['schedule']})")
        except Exception as e:
            logger.error(f"Error scheduling workflow: {str(e)}")
    
    def execute_workflow(self, workflow_id: str, params: Dict = None) -> Dict:
        """
        Execute a workflow
        
        Args:
            workflow_id: Workflow ID
            params: Additional parameters
            
        Returns:
            Execution result
        """
        try:
            workflow = self.workflows.get(workflow_id)
            if not workflow:
                raise Exception(f"Workflow not found: {workflow_id}")
            
            if not workflow["enabled"]:
                logger.info(f"Workflow disabled, skipping: {workflow['name']}")
                return {"success": False, "error": "Workflow disabled"}
            
            logger.info(f"Executing workflow: {workflow['name']}")
            
            # Update workflow stats
            workflow["last_run"] = datetime.now().isoformat()
            workflow["run_count"] += 1
            
            # Initialize context for workflow execution
            context = {
                "workflow_id": workflow_id,
                "start_time": datetime.now(),
                "params": params or {},
                "results": {},
                "errors": []
            }
            
            # Execute steps
            for i, step in enumerate(workflow["steps"]):
                logger.info(f"  Step {i+1}/{len(workflow['steps'])}: {step['action']}")
                
                try:
                    # Execute action
                    result = self._execute_action(step, context)
                    context["results"][step['action']] = result
                    
                    # Check for errors
                    if isinstance(result, dict) and not result.get("success", True):
                        context["errors"].append({
                            "step": step['action'],
                            "error": result.get("error", "Unknown error")
                        })
                        
                        # Check if step is critical
                        if step.get("critical", True):
                            raise Exception(f"Critical step failed: {step['action']}")
                
                except Exception as e:
                    logger.error(f"Step failed: {step['action']} - {str(e)}")
                    context["errors"].append({
                        "step": step['action"'],
                        "error": str(e)
                    })
                    
                    if step.get("critical", True):
                        raise
            
            # Update success stats
            workflow["success_count"] += 1
            
            # Save updated workflow
            self.save_workflow(workflow)
            
            # Log execution
            self._log_execution(workflow_id, context)
            
            logger.info(f"✅ Workflow completed: {workflow['name']}")
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "execution_time": (datetime.now() - context["start_time"]).total_seconds(),
                "results": context["results"],
                "errors": context["errors"]
            }
            
        except Exception as e:
            logger.error(f"❌ Workflow execution failed: {str(e)}")
            
            # Update failure stats
            if workflow_id in self.workflows:
                workflow = self.workflows[workflow_id]
                workflow["failure_count"] += 1
                self.save_workflow(workflow)
            
            return {
                "success": False,
                "workflow_id": workflow_id,
                "error": str(e)
            }
    
    def _execute_action(self, step: Dict, context: Dict) -> Dict:
        """Execute a single workflow action"""
        action = step["action"]
        params = {**step.get("params", {}), **context.get("params", {})}
        
        # Get handler for action
        handler = self.action_handlers.get(action)
        if not handler:
            raise Exception(f"Unknown action: {action}")
        
        # Execute handler
        return handler(params, context)
    
    def _handle_scrape_trending(self, params: Dict, context: Dict) -> Dict:
        """Handle trending topics scraping"""
        try:
            from scraper.trending_scraper import TrendingScraper
            scraper = TrendingScraper()
            
            result = scraper.scrape_trending_topics(
                sources=params.get("sources", ["youtube"]),
                category=params.get("category", "all"),
                max_results=params.get("max_results", 10)
            )
            
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _handle_generate_script(self, params: Dict, context: Dict) -> Dict:
        """Handle script generation"""
        try:
            from ai_engine.script_generator import HindiScriptGenerator
            generator = HindiScriptGenerator()
            
            topic = params.get("topic")
            if not topic:
                # Get from previous step
                trending_result = context["results"].get("scrape_trending", {})
                if trending_result.get("success") and trending_result.get("topics"):
                    topic = trending_result["topics"][0]["title"]
                else:
                    raise Exception("No topic provided for script generation")
            
            result = generator.generate_script(
                topic=topic,
                category=params.get("category", "motivation"),
                duration=params.get("duration", 60),
                tone=params.get("tone", "motivational")
            )
            
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _handle_generate_images(self, params: Dict, context: Dict) -> Dict:
        """Handle image generation"""
        try:
            from ai_engine.image_generator import HindiImageGenerator
            generator = HindiImageGenerator()
            
            # Get script from context
            script_result = context["results"].get("generate_script", {})
            if not script_result.get("success"):
                raise Exception("No script available for image generation")
            
            script = script_result["script"]
            image_paths = []
            
            for i, scene in enumerate(script["scenes"]):
                result = generator.generate_scene_image(
                    prompt=scene.get("visual_prompt", scene["narration"]),
                    scene_number=i + 1,
                    category=script.get("category", "motivation")
                )
                
                if result.get("success"):
                    image_paths.append(result)
            
            return {"success": True, "image_paths": image_paths}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _handle_generate_voice(self, params: Dict, context: Dict) -> Dict:
        """Handle voice generation"""
        try:
            from ai_engine.voice_generator import HindiVoiceGenerator
            generator = HindiVoiceGenerator()
            
            # Get script from context
            script_result = context["results"].get("generate_script", {})
            if not script_result.get("success"):
                raise Exception("No script available for voice generation")
            
            script = script_result["script"]
            voice_paths = []
            
            for i, scene in enumerate(script["scenes"]):
                result = generator.generate_scene_voice(
                    text=scene["narration"],
                    scene_number=i + 1,
                    voice_type=params.get("voice_type", "neutral")
                )
                
                if result.get("success"):
                    voice_paths.append(result)
            
            return {"success": True, "voice_paths": voice_paths}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _handle_compose_video(self, params: Dict, context: Dict) -> Dict:
        """Handle video composition"""
        try:
            from ai_engine.cinematic_video_composer import CinematicVideoComposer
            composer = CinematicVideoComposer()
            
            # Save script to file
            script_result = context["results"].get("generate_script", {})
            if not script_result.get("success"):
                raise Exception("No script available for video composition")
            
            import json
            script_path = f"temp/script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.makedirs("temp", exist_ok=True)
            
            with open(script_path, 'w', encoding='utf-8') as f:
                json.dump(script_result["script"], f, ensure_ascii=False, indent=2)
            
            # Compose video
            output_path = params.get("output_path", f"output/videos/video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
            
            success = composer.compose_cinematic_video(
                script_path=script_path,
                output_path=output_path,
                platform=params.get("platform", "youtube_shorts"),
                music_path=params.get("music_path"),
                color_preset=params.get("color_preset", "cinematic_blue")
            )
            
            return {"success": success, "video_path": output_path if success else None}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _handle_cinematic_generation(self, params: Dict, context: Dict) -> Dict:
        """Handle complete cinematic generation"""
        try:
            from main_cinematic_coordinator import CinematicAIFactory
            factory = CinematicAIFactory()
            
            # Get topic from context or params
            topic = params.get("topic")
            if not topic:
                trending_result = context["results"].get("scrape_trending", {})
                if trending_result.get("success") and trending_result.get("topics"):
                    topic = trending_result["topics"][0]["title"]
                else:
                    raise Exception("No topic provided for generation")
            
            result = factory.generate_cinematic_content(
                topic=topic,
                category=params.get("category", "motivation"),
                platform=params.get("platform", "youtube_shorts"),
                duration=params.get("duration", 60)
            )
            
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _handle_publish(self, params: Dict, context: Dict) -> Dict:
        """Handle publishing to platforms"""
        try:
            # This would integrate with publisher modules
            platforms = params.get("platforms", ["youtube"])
            auto_publish = params.get("auto_publish", False)
            
            # Get video path from context
            video_result = context["results"].get("compose_video", {})
            if not video_result.get("success"):
                raise Exception("No video available for publishing")
            
            video_path = video_result["video_path"]
            
            # TODO: Implement actual publishing logic
            # For now, just return success
            return {
                "success": True,
                "platforms": platforms,
                "auto_publish": auto_publish,
                "video_path": video_path
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _handle_notify(self, params: Dict, context: Dict) -> Dict:
        """Handle notifications"""
        try:
            message = params.get("message", "Workflow notification")
            level = params.get("level", "info")
            
            # Log notification
            logger.info(f"NOTIFICATION [{level.upper()}]: {message}")
            
            # TODO: Add email/Discord/Slack notifications
            
            return {"success": True, "message": message}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _handle_delay(self, params: Dict, context: Dict) -> Dict:
        """Handle delays between steps"""
        try:
            seconds = params.get("seconds", 1)
            time.sleep(seconds)
            return {"success": True, "delayed": seconds}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _log_execution(self, workflow_id: str, context: Dict):
        """Log workflow execution"""
        try:
            log_entry = {
                "workflow_id": workflow_id,
                "timestamp": datetime.now().isoformat(),
                "execution_time": (datetime.now() - context["start_time"]).total_seconds(),
                "results": context["results"],
                "errors": context["errors"]
            }
            
            log_file = Path("logs/workflows") / f"{workflow_id}_{datetime.now().strftime('%Y%m%d')}.json"
            
            # Append to log file
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            logs.append(log_entry)
            
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
        
        except Exception as e:
            logger.error(f"Error logging execution: {str(e)}")
    
    def start(self):
        """Start the workflow scheduler"""
        if self.is_running:
            logger.warning("Workflow engine already running")
            return
        
        self.is_running = True
        self.worker_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.worker_thread.start()
        
        logger.info("🚀 Workflow engine started")
    
    def stop(self):
        """Stop the workflow scheduler"""
        self.is_running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        
        logger.info("⏹️ Workflow engine stopped")
    
    def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.is_running:
            try:
                self.scheduler.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.error(f"Scheduler error: {str(e)}")
                time.sleep(60)  # Wait before retrying


def main():
    """Test workflow engine"""
    engine = WorkflowEngine()
    
    # Create a test workflow
    workflow_id = engine.create_workflow(
        name="Cinematic Test Workflow",
        description="Test cinematic content generation",
        trigger="manual",
        steps=[
            {
                "action": "scrape_trending",
                "params": {
                    "sources": ["youtube"],
                    "category": "motivation",
                    "max_results": 3
                },
                "critical": False
            },
            {
                "action": "generate_cinematic_content",
                "params": {
                    "category": "motivation",
                    "platform": "youtube_shorts",
                    "duration": 60
                },
                "critical": True
            }
        ]
    )
    
    print(f"Created workflow: {workflow_id}")
    
    # Execute workflow
    result = engine.execute_workflow(workflow_id)
    print(f"Workflow result: {result}")


if __name__ == "__main__":
    main()