import os
import asyncio
import asyncpg
import redis
from datetime import datetime, timedelta
from dotenv import load_dotenv
from scrapers.youtube_scraper import YouTubeScraper
from scrapers.news_scraper import NewsScraper
from scrapers.twitter_scraper import TwitterScraper
from scrapers.reddit_scraper import RedditScraper
from scrapers.google_trends import GoogleTrendsScraper
from utils.proxy_manager import ProxyManager
from utils.topic_ranker import TopicRanker
from utils.database import Database
from utils.logger import setup_logger

load_dotenv()

class ScraperEngine:
    def __init__(self):
        self.logger = setup_logger('scraper-engine')
        self.db = Database()
        self.redis_client = redis.Redis.from_url(
            os.getenv('REDIS_URL', 'redis://localhost:6379'),
            decode_responses=True
        )
        self.proxy_manager = ProxyManager()
        self.topic_ranker = TopicRanker()
        
        # Initialize scrapers
        self.scrapers = {
            'youtube': YouTubeScraper(self.proxy_manager),
            'news': NewsScraper(self.proxy_manager),
            'twitter': TwitterScraper(self.proxy_manager),
            'reddit': RedditScraper(self.proxy_manager),
            'google_trends': GoogleTrendsScraper(self.proxy_manager),
        }
        
        self.is_running = False
    
    async def start(self):
        """Start the scraper engine"""
        self.logger.info("Starting Scraper Engine...")
        self.is_running = True
        
        # Connect to database
        await self.db.connect()
        
        # Start scraping loops for each source
        tasks = [
            self.scrape_youtube_loop(),
            self.scrape_news_loop(),
            self.scrape_twitter_loop(),
            self.scrape_reddit_loop(),
            self.scrape_google_trends_loop(),
        ]
        
        await asyncio.gather(*tasks)
    
    async def stop(self):
        """Stop the scraper engine"""
        self.logger.info("Stopping Scraper Engine...")
        self.is_running = False
        await self.db.close()
    
    async def scrape_youtube_loop(self):
        """Scrape YouTube trending videos every 15 minutes"""
        while self.is_running:
            try:
                self.logger.info("Scraping YouTube trending videos...")
                
                topics = await self.scrapers['youtube'].scrape_trending()
                ranked_topics = self.topic_ranker.rank_topics(topics)
                
                # Save to database
                for topic in ranked_topics:
                    await self.db.save_topic(topic)
                
                self.logger.info(f"Saved {len(ranked_topics)} YouTube topics")
                
                # Wait 15 minutes
                await asyncio.sleep(900)
                
            except Exception as e:
                self.logger.error(f"YouTube scraping error: {str(e)}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def scrape_news_loop(self):
        """Scrape news articles every 30 minutes"""
        while self.is_running:
            try:
                self.logger.info("Scraping news articles...")
                
                topics = await self.scrapers['news'].scrape_trending()
                ranked_topics = self.topic_ranker.rank_topics(topics)
                
                # Save to database
                for topic in ranked_topics:
                    await self.db.save_topic(topic)
                
                self.logger.info(f"Saved {len(ranked_topics)} news topics")
                
                # Wait 30 minutes
                await asyncio.sleep(1800)
                
            except Exception as e:
                self.logger.error(f"News scraping error: {str(e)}")
                await asyncio.sleep(300)
    
    async def scrape_twitter_loop(self):
        """Scrape Twitter trending topics every 10 minutes"""
        while self.is_running:
            try:
                self.logger.info("Scraping Twitter trends...")
                
                topics = await self.scrapers['twitter'].scrape_trending()
                ranked_topics = self.topic_ranker.rank_topics(topics)
                
                # Save to database
                for topic in ranked_topics:
                    await self.db.save_topic(topic)
                
                self.logger.info(f"Saved {len(ranked_topics)} Twitter topics")
                
                # Wait 10 minutes
                await asyncio.sleep(600)
                
            except Exception as e:
                self.logger.error(f"Twitter scraping error: {str(e)}")
                await asyncio.sleep(300)
    
    async def scrape_reddit_loop(self):
        """Scrape Reddit trending posts every 20 minutes"""
        while self.is_running:
            try:
                self.logger.info("Scraping Reddit trending posts...")
                
                topics = await self.scrapers['reddit'].scrape_trending()
                ranked_topics = self.topic_ranker.rank_topics(topics)
                
                # Save to database
                for topic in ranked_topics:
                    await self.db.save_topic(topic)
                
                self.logger.info(f"Saved {len(ranked_topics)} Reddit topics")
                
                # Wait 20 minutes
                await asyncio.sleep(1200)
                
            except Exception as e:
                self.logger.error(f"Reddit scraping error: {str(e)}")
                await asyncio.sleep(300)
    
    async def scrape_google_trends_loop(self):
        """Scrape Google Trends every hour"""
        while self.is_running:
            try:
                self.logger.info("Scraping Google Trends...")
                
                topics = await self.scrapers['google_trends'].scrape_trending()
                ranked_topics = self.topic_ranker.rank_topics(topics)
                
                # Save to database
                for topic in ranked_topics:
                    await self.db.save_topic(topic)
                
                self.logger.info(f"Saved {len(ranked_topics)} Google Trends topics")
                
                # Wait 1 hour
                await asyncio.sleep(3600)
                
            except Exception as e:
                self.logger.error(f"Google Trends scraping error: {str(e)}")
                await asyncio.sleep(300)
    
    async def manual_scrape(self, source: str, **kwargs):
        """Manually trigger scraping for a specific source"""
        if source not in self.scrapers:
            raise ValueError(f"Unknown source: {source}")
        
        self.logger.info(f"Manually scraping {source}...")
        
        topics = await self.scrapers[source].scrape_trending(**kwargs)
        ranked_topics = self.topic_ranker.rank_topics(topics)
        
        # Save to database
        saved_count = 0
        for topic in ranked_topics:
            try:
                await self.db.save_topic(topic)
                saved_count += 1
            except Exception as e:
                self.logger.warning(f"Failed to save topic: {str(e)}")
        
        self.logger.info(f"Manually saved {saved_count} topics from {source}")
        
        return {
            "source": source,
            "topics_found": len(topics),
            "topics_saved": saved_count
        }

if __name__ == "__main__":
    engine = ScraperEngine()
    
    try:
        asyncio.run(engine.start())
    except KeyboardInterrupt:
        asyncio.run(engine.stop())
    except Exception as e:
        print(f"Fatal error: {str(e)}")
