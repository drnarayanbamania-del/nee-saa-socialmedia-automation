import { logger } from '../utils/logger';
import { AIService } from '../services/ai-service';
import { ScraperService } from '../services/scraper-service';
import { VideoService } from '../services/video-service';
import { PublishingService } from '../services/publishing-service';
import { db } from '../index';

export interface WorkflowStep {
  id: string;
  type: 'scrape' | 'generate-script' | 'generate-image' | 'generate-voice' | 'compose-video' | 'publish';
  config: Record<string, any>;
  dependsOn?: string[];
}

export interface WorkflowConfig {
  steps: WorkflowStep[];
  metadata?: Record<string, any>;
}

export interface WorkflowResult {
  success: boolean;
  data: Record<string, any>;
  errors: string[];
}

export class AutomationWorkflow {
  private config: WorkflowConfig;
  private userId: string;
  private results: Map<string, any> = new Map();
  private errors: string[] = [];
  
  private aiService: AIService;
  private scraperService: ScraperService;
  private videoService: VideoService;
  private publishingService: PublishingService;

  constructor(jobData: any) {
    this.config = jobData.workflowConfig;
    this.userId = jobData.userId;
    
    this.aiService = new AIService();
    this.scraperService = new ScraperService();
    this.videoService = new VideoService();
    this.publishingService = new PublishingService();
  }

  async execute(): Promise<WorkflowResult> {
    logger.info(`Starting workflow execution for user ${this.userId}`);
    
    try {
      // Execute steps in order
      for (const step of this.config.steps) {
        const canExecute = this.canExecuteStep(step);
        
        if (!canExecute) {
          this.errors.push(`Cannot execute step ${step.id}: dependencies not met`);
          continue;
        }

        logger.info(`Executing step: ${step.id} (${step.type})`);
        
        try {
          const result = await this.executeStep(step);
          this.results.set(step.id, result);
          
          logger.info(`Step ${step.id} completed successfully`);
        } catch (error) {
          const errorMessage = `Step ${step.id} failed: ${error.message}`;
          logger.error(errorMessage);
          this.errors.push(errorMessage);
          
          // Continue or stop based on step configuration
          if (step.config.stopOnError !== false) {
            break;
          }
        }
      }

      // Save workflow results
      await this.saveResults();

      return {
        success: this.errors.length === 0,
        data: Object.fromEntries(this.results),
        errors: this.errors,
      };
    } catch (error) {
      logger.error('Workflow execution failed:', error);
      
      return {
        success: false,
        data: Object.fromEntries(this.results),
        errors: [...this.errors, error.message],
      };
    }
  }

  private canExecuteStep(step: WorkflowStep): boolean {
    if (!step.dependsOn || step.dependsOn.length === 0) {
      return true;
    }

    return step.dependsOn.every(dep => this.results.has(dep));
  }

  private async executeStep(step: WorkflowStep): Promise<any> {
    switch (step.type) {
      case 'scrape':
        return await this.executeScrapeStep(step);
      
      case 'generate-script':
        return await this.executeScriptGenerationStep(step);
      
      case 'generate-image':
        return await this.executeImageGenerationStep(step);
      
      case 'generate-voice':
        return await this.executeVoiceGenerationStep(step);
      
      case 'compose-video':
        return await this.executeVideoCompositionStep(step);
      
      case 'publish':
        return await this.executePublishingStep(step);
      
      default:
        throw new Error(`Unknown step type: ${step.type}`);
    }
  }

  private async executeScrapeStep(step: WorkflowStep): Promise<any> {
    const { source, keywords, limit } = step.config;
    
    const topics = await this.scraperService.scrapeTrendingTopics(source, {
      keywords,
      limit: limit || 10,
    });
    
    // Save topics to database
    for (const topic of topics) {
      await db.saveTopic({
        userId: this.userId,
        ...topic,
      });
    }
    
    return topics;
  }

  private async executeScriptGenerationStep(step: WorkflowStep): Promise<any> {
    const { topic, duration, tone, platform } = step.config;
    
    // Get topic data if reference
    let topicData = topic;
    if (topic.startsWith('$')) {
      const refStep = topic.substring(1);
      const scrapedData = this.results.get(refStep);
      topicData = scrapedData[0]?.title || topic;
    }
    
    const script = await this.aiService.generateScript({
      topic: topicData,
      duration,
      tone,
      platform,
    });
    
    if (!script.success) {
      throw new Error(script.error);
    }
    
    // Save script to database
    const scriptId = await db.saveScript({
      userId: this.userId,
      title: script.script.title,
      content: script.script.scenes[0]?.narration || '',
      scenes: script.script.scenes,
      hook: script.script.hook,
      duration: script.script.duration_estimate,
      tone,
    });
    
    return {
      ...script,
      scriptId,
    };
  }

  private async executeImageGenerationStep(step: WorkflowStep): Promise<any> {
    const { prompt, style, sceneNumber } = step.config;
    
    // Get prompt from reference if needed
    let imagePrompt = prompt;
    if (prompt.startsWith('$')) {
      const refStep = prompt.substring(1);
      const scriptData = this.results.get(refStep);
      
      if (sceneNumber !== undefined && scriptData?.script?.scenes?.[sceneNumber]) {
        imagePrompt = scriptData.script.scenes[sceneNumber].visual_description;
      } else {
        imagePrompt = scriptData?.script?.scenes?.[0]?.visual_description || prompt;
      }
    }
    
    const image = await this.aiService.generateImage({
      prompt: imagePrompt,
      style,
      sceneNumber,
    });
    
    if (!image.success) {
      throw new Error(image.error);
    }
    
    // Save image to database
    const imageId = await db.saveImage({
      userId: this.userId,
      prompt: imagePrompt,
      imageUrl: image.image_url,
      style,
      sceneNumber,
    });
    
    return {
      ...image,
      imageId,
    };
  }

  private async executeVoiceGenerationStep(step: WorkflowStep): Promise<any> {
    const { text, voiceId, settings } = step.config;
    
    // Get text from reference if needed
    let voiceText = text;
    if (text.startsWith('$')) {
      const refStep = text.substring(1);
      const scriptData = this.results.get(refStep);
      
      // Combine all narration text
      voiceText = scriptData?.script?.scenes
        ?.map((scene: any) => scene.narration)
        .join(' ') || text;
    }
    
    const voice = await this.aiService.generateVoice({
      text: voiceText,
      voiceId,
      settings,
    });
    
    if (!voice.success) {
      throw new Error(voice.error);
    }
    
    // Save voice file to database
    const voiceId_db = await db.saveVoiceFile({
      userId: this.userId,
      text: voiceText,
      voiceUrl: voice.voice_url,
      voiceId: voice.voice_id,
      duration: voice.duration,
    });
    
    return {
      ...voice,
      voiceId: voiceId_db,
    };
  }

  private async executeVideoCompositionStep(step: WorkflowStep): Promise<any> {
    const { scriptId, imageId, voiceId, options } = step.config;
    
    // Resolve references
    const resolvedScriptId = scriptId.startsWith('$') ? 
      this.results.get(scriptId.substring(1))?.scriptId : scriptId;
    
    const resolvedImageId = imageId.startsWith('$') ? 
      this.results.get(imageId.substring(1))?.imageId : imageId;
    
    const resolvedVoiceId = voiceId.startsWith('$') ? 
      this.results.get(voiceId.substring(1))?.voiceId : voiceId;
    
    const video = await this.videoService.composeVideo({
      scriptId: resolvedScriptId,
      imageId: resolvedImageId,
      voiceId: resolvedVoiceId,
      options,
    });
    
    if (!video.success) {
      throw new Error(video.error);
    }
    
    // Save video to database
    const videoId = await db.saveVideo({
      userId: this.userId,
      scriptId: resolvedScriptId,
      imageId: resolvedImageId,
      voiceId: resolvedVoiceId,
      title: video.title,
      videoUrl: video.video_url,
      duration: video.duration,
      resolution: options?.resolution || '1080p',
    });
    
    return {
      ...video,
      videoId,
    };
  }

  private async executePublishingStep(step: WorkflowStep): Promise<any> {
    const { videoId, platform, schedule } = step.config;
    
    // Resolve reference
    const resolvedVideoId = videoId.startsWith('$') ? 
      this.results.get(videoId.substring(1))?.videoId : videoId;
    
    // Get video and related data
    const video = await db.getVideo(resolvedVideoId);
    const script = await db.getScript(video.script_id);
    
    // Generate captions and hashtags if not provided
    if (!step.config.caption) {
      const captions = await this.aiService.generateCaptionsAndHashtags(
        script.content,
        platform
      );
      
      step.config.caption = captions.captions.caption;
      step.config.hashtags = captions.captions.hashtags;
    }
    
    // Publish or schedule
    const publishData = {
      videoId: resolvedVideoId,
      platform,
      title: video.title,
      description: step.config.caption,
      tags: step.config.hashtags,
      scheduledAt: schedule,
    };
    
    let result;
    if (schedule && new Date(schedule) > new Date()) {
      result = await this.publishingService.schedulePublish(publishData);
    } else {
      result = await this.publishingService.publish(publishData);
    }
    
    if (!result.success) {
      throw new Error(result.error);
    }
    
    // Save publishing record
    await db.savePublishedContent({
      userId: this.userId,
      videoId: resolvedVideoId,
      platform,
      platformPostId: result.postId,
      title: video.title,
      description: step.config.caption,
      tags: step.config.hashtags,
      scheduledAt: schedule,
    });
    
    return result;
  }

  private async saveResults(): Promise<void> {
    // Save workflow execution results to database
    await db.saveWorkflowExecution({
      userId: this.userId,
      config: this.config,
      results: Object.fromEntries(this.results),
      errors: this.errors,
      success: this.errors.length === 0,
    });
  }
}