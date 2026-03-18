import express from 'express';
import { QueueScheduler, Queue, Worker } from 'bullmq';
import { Redis } from 'ioredis';
import cron from 'node-cron';
import { config } from './config';
import { AutomationWorkflow } from './workflows/workflow';
import { Database } from './database';
import { logger } from './utils/logger';
import { workflowRouter } from './routes/workflow';
import { jobRouter } from './routes/jobs';

const app = express();
const port = config.port;

// Middleware
app.use(express.json());

// Redis connection
export const redis = new Redis(config.redis.url);
export const redisPublisher = new Redis(config.redis.url);

// Database connection
export const db = new Database();

// Initialize queues
export const workflowQueue = new Queue('workflow-queue', {
  connection: redis,
  defaultJobOptions: {
    attempts: 3,
    backoff: {
      type: 'exponential',
      delay: 2000,
    },
  },
});

export const schedulerQueue = new Queue('scheduler-queue', {
  connection: redis,
});

// Queue schedulers
new QueueScheduler('workflow-queue', { connection: redis });
new QueueScheduler('scheduler-queue', { connection: redis });

// Initialize worker
const worker = new Worker(
  'workflow-queue',
  async (job) => {
    logger.info(`Processing job ${job.id} - ${job.name}`);
    
    const workflow = new AutomationWorkflow(job.data);
    const result = await workflow.execute();
    
    return result;
  },
  {
    connection: redis,
    concurrency: 5,
  }
);

// Worker event handlers
worker.on('completed', (job) => {
  logger.info(`Job ${job.id} completed successfully`);
  
  // Update job execution in database
  db.updateJobExecution(job.id as string, 'completed', null, job.returnvalue);
});

worker.on('failed', (job, err) => {
  logger.error(`Job ${job?.id} failed: ${err.message}`);
  
  // Update job execution in database
  if (job) {
    db.updateJobExecution(job.id as string, 'failed', err.message, null);
  }
});

// Routes
app.use('/api/v1/workflows', workflowRouter);
app.use('/api/v1/jobs', jobRouter);

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    queues: {
      workflow: 'connected',
      scheduler: 'connected',
    },
    redis: redis.status,
  });
});

// Start cron scheduler for recurring jobs
async function startScheduler() {
  logger.info('Starting automation scheduler...');
  
  // Run every minute to check for scheduled jobs
  cron.schedule('* * * * *', async () => {
    try {
      const jobs = await db.getActiveScheduledJobs();
      
      for (const job of jobs) {
        const shouldRun = await db.shouldJobRun(job.id);
        
        if (shouldRun) {
          logger.info(`Scheduling job ${job.id} - ${job.name}`);
          
          await workflowQueue.add(job.name, {
            jobId: job.id,
            userId: job.user_id,
            workflowConfig: job.workflow_config,
          }, {
            jobId: `job-${job.id}-${Date.now()}`,
          });
          
          await db.updateJobLastRun(job.id);
        }
      }
    } catch (error) {
      logger.error('Scheduler error:', error);
    }
  });
}

// Graceful shutdown
process.on('SIGTERM', async () => {
  logger.info('SIGTERM received, shutting down gracefully...');
  
  await worker.close();
  await workflowQueue.close();
  await schedulerQueue.close();
  await redis.quit();
  await redisPublisher.quit();
  await db.close();
  
  process.exit(0);
});

// Start server
async function start() {
  try {
    await db.connect();
    await startScheduler();
    
    app.listen(port, () => {
      logger.info(`Automation Engine running on port ${port}`);
      logger.info(`Worker concurrency: 5 jobs`);
    });
  } catch (error) {
    logger.error('Failed to start server:', error);
    process.exit(1);
  }
}

start();

export default app;
