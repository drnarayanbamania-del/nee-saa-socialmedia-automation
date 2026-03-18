"""
Hindi Trending Topics Scraper
Collects trending topics from multiple sources in Hindi
"""

import requests
import json
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
import re
import os
from urllib.parse import quote_plus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TrendingTopic:
    topic: str
    source: str
    category: str
    hindi_category: str
    trending_score: float
    metadata: Dict
    created_at: datetime

class HindiTrendingScraper:
    """
    Scrape trending topics from various sources in Hindi
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Hindi content categories
        self.categories = {
            "motivation": {
                "en": "motivation",
                "hi": "प्रेरणा",
                "keywords": ["motivation", "success", "habits", "morning routine", "discipline"]
            },
            "education": {
                "en": "education",
                "hi": "शिक्षा", 
                "keywords": ["learning", "study", "education", "knowledge", "tips"]
            },
            "business": {
                "en": "business",
                "hi": "व्यापार",
                "keywords": ["business", "startup", "entrepreneur", "money", "investing"]
            },
            "technology": {
                "en": "technology",
                "hi": "प्रौद्योगिकी",
                "keywords": ["technology", "tech", "AI", "digital", "innovation"]
            },
            "lifestyle": {
                "en": "lifestyle",
                "hi": "जीवनशैली",
                "keywords": ["lifestyle", "health", "fitness", "wellness", "selfcare"]
            },
            "entertainment": {
                "en": "entertainment",
                "hi": "मनोरंजन",
                "keywords": ["entertainment", "trending", "viral", "fun", "comedy"]
            }
        }
    
    def scrape_youtube_trending(self) -> List[TrendingTopic]:
        """
        Scrape trending topics from YouTube (simulated - in production use YouTube API)
        """
        try:
            logger.info("Scraping YouTube trending topics")
            
            # Simulated trending topics (in production, use YouTube Data API)
            trending_topics = [
                {
                    "topic": "morning routine for success",
                    "hindi_topic": "सफलता के लिए सुबह की रूटीन",
                    "category": "motivation",
                    "views": "10M",
                    "trending_score": 95
                },
                {
                    "topic": "5 habits of millionaires",
                    "hindi_topic": "अमीर लोगों की 5 आदतें",
                    "category": "business",
                    "views": "8M", 
                    "trending_score": 90
                },
                {
                    "topic": "study tips for students",
                    "hindi_topic": "स्टूडेंट्स के लिए पढ़ाई के टिप्स",
                    "category": "education",
                    "views": "5M",
                    "trending_score": 85
                }
            ]
            
            topics = []
            for item in trending_topics:
                category_info = self.categories.get(item["category"], self.categories["motivation"])
                
                topic = TrendingTopic(
                    topic=item["topic"],
                    source="youtube",
                    category=item["category"],
                    hindi_category=category_info["hi"],
                    trending_score=item["trending_score"],
                    metadata={
                        "hindi_topic": item["hindi_topic"],
                        "views": item["views"],
                        "platform": "youtube"
                    },
                    created_at=datetime.now()
                )
                topics.append(topic)
            
            logger.info(f"Found {len(topics)} trending topics from YouTube")
            return topics
            
        except Exception as e:
            logger.error(f"Error scraping YouTube: {str(e)}")
            return []
    
    def scrape_google_trends(self) -> List[TrendingTopic]:
        """
        Scrape trending searches from Google Trends (simulated)
        """
        try:
            logger.info("Scraping Google trends")
            
            # Simulated Google trends for India/Hindi
            trending_searches = [
                {
                    "topic": "how to start business",
                    "hindi_topic": "बिजनेस कैसे शुरू करें",
                    "category": "business",
                    "search_volume": 10000,
                    "growth": 150
                },
                {
                    "topic": "healthy breakfast ideas",
                    "hindi_topic": "स्वस्थ नाश्ता आइडियाज",
                    "category": "lifestyle",
                    "search_volume": 8000,
                    "growth": 120
                },
                {
                    "topic": "productivity tips",
                    "hindi_topic": "प्रोडक्टिविटी टिप्स",
                    "category": "motivation",
                    "search_volume": 7500,
                    "growth": 110
                }
            ]
            
            topics = []
            for item in trending_searches:
                category_info = self.categories.get(item["category"], self.categories["motivation"])
                
                trending_score = min(100, (item["search_volume"] / 100) + item["growth"])
                
                topic = TrendingTopic(
                    topic=item["topic"],
                    source="google_trends",
                    category=item["category"],
                    hindi_category=category_info["hi"],
                    trending_score=trending_score,
                    metadata={
                        "hindi_topic": item["hindi_topic"],
                        "search_volume": item["search_volume"],
                        "growth": item["growth"]
                    },
                    created_at=datetime.now()
                )
                topics.append(topic)
            
            logger.info(f"Found {len(topics)} trending topics from Google Trends")
            return topics
            
        except Exception as e:
            logger.error(f"Error scraping Google Trends: {str(e)}")
            return []
    
    def scrape_twitter_trending(self) -> List[TrendingTopic]:
        """
        Scrape trending topics from Twitter/X (simulated)
        """
        try:
            logger.info("Scraping Twitter trending topics")
            
            # Simulated Twitter trends
            twitter_trends = [
                {
                    "topic": "digital marketing tips",
                    "hindi_topic": "डिजिटल मार्केटिंग टिप्स",
                    "category": "business",
                    "tweets": 50000,
                    "rank": 1
                },
                {
                    "topic": "fitness challenge",
                    "hindi_topic": "फिटनेस चैलेंज",
                    "category": "lifestyle",
                    "tweets": 35000,
                    "rank": 2
                },
                {
                    "topic": "study motivation",
                    "hindi_topic": "पढ़ाई की प्रेरणा",
                    "category": "education",
                    "tweets": 28000,
                    "rank": 3
                }
            ]
            
            topics = []
            for item in twitter_trends:
                category_info = self.categories.get(item["category"], self.categories["motivation"])
                
                trending_score = min(100, item["tweets"] / 1000)
                
                topic = TrendingTopic(
                    topic=item["topic"],
                    source="twitter",
                    category=item["category"],
                    hindi_category=category_info["hi"],
                    trending_score=trending_score,
                    metadata={
                        "hindi_topic": item["hindi_topic"],
                        "tweets": item["tweets"],
                        "rank": item["rank"]
                    },
                    created_at=datetime.now()
                )
                topics.append(topic)
            
            logger.info(f"Found {len(topics)} trending topics from Twitter")
            return topics
            
        except Exception as e:
            logger.error(f"Error scraping Twitter: {str(e)}")
            return []
    
    def scrape_news_headlines(self) -> List[TrendingTopic]:
        """
        Scrape trending news headlines (simulated)
        """
        try:
            logger.info("Scraping news headlines")
            
            # Simulated news headlines
            news_topics = [
                {
                    "topic": "ai technology impact",
                    "hindi_topic": "एआई टेक्नोलॉजी का प्रभाव",
                    "category": "technology",
                    "headline": "AI changing job market",
                    "hindi_headline": "एआई नौकरी के बाजार को बदल रहा है"
                },
                {
                    "topic": "startup funding news",
                    "hindi_topic": "स्टार्टअप फंडिंग न्यूज",
                    "category": "business",
                    "headline": "Indian startups raise $1B",
                    "hindi_headline": "भारतीय स्टार्टअप्स ने 1 बिलियन डॉलर जुटाए"
                }
            ]
            
            topics = []
            for item in news_topics:
                category_info = self.categories.get(item["category"], self.categories["motivation"])
                
                topic = TrendingTopic(
                    topic=item["topic"],
                    source="news",
                    category=item["category"],
                    hindi_category=category_info["hi"],
                    trending_score=80,
                    metadata={
                        "hindi_topic": item["hindi_topic"],
                        "headline": item["headline"],
                        "hindi_headline": item["hindi_headline"]
                    },
                    created_at=datetime.now()
                )
                topics.append(topic)
            
            logger.info(f"Found {len(topics)} trending topics from News")
            return topics
            
        except Exception as e:
            logger.error(f"Error scraping news: {str(e)}")
            return []

    def _infer_category(self, text: str) -> str:
        text_lower = text.lower()
        for key, config in self.categories.items():
            if any(keyword.lower() in text_lower for keyword in config["keywords"]):
                return key
        return "entertainment"

    def _youtube_fallback_items(self) -> List[Dict]:
        return [
            {
                "title": "Morning Routine Secrets of High Performers",
                "hindi_topic": "हाई परफॉर्मर्स की सुबह की सीक्रेट रूटीन",
                "channel": "Growth Lab",
                "views": "12M",
                "duration": "0:58",
                "published": "2 days ago",
                "url": "https://www.youtube.com/results?search_query=" + quote_plus("Morning Routine Secrets of High Performers"),
                "thumbnail": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=800&q=80",
                "score": 97,
            },
            {
                "title": "AI Tools That Will Replace Old Workflows",
                "hindi_topic": "एआई टूल्स जो पुराने वर्कफ्लो को बदल देंगे",
                "channel": "Tech Pulse",
                "views": "8.4M",
                "duration": "1:12",
                "published": "1 day ago",
                "url": "https://www.youtube.com/results?search_query=" + quote_plus("AI Tools That Will Replace Old Workflows"),
                "thumbnail": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?auto=format&fit=crop&w=800&q=80",
                "score": 93,
            },
            {
                "title": "How to Earn With Faceless Shorts Channels",
                "hindi_topic": "फेसलेस शॉर्ट्स चैनल से कमाई कैसे करें",
                "channel": "Creator Stack",
                "views": "6.9M",
                "duration": "0:45",
                "published": "3 days ago",
                "url": "https://www.youtube.com/results?search_query=" + quote_plus("How to Earn With Faceless Shorts Channels"),
                "thumbnail": "https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=800&q=80",
                "score": 90,
            },
        ]

    def _instagram_fallback_items(self) -> List[Dict]:
        return [
            {
                "title": "3 Reel Hooks That Instantly Boost Watch Time",
                "hindi_topic": "3 रील हुक्स जो वॉच टाइम तुरंत बढ़ाते हैं",
                "creator": "@growthreels",
                "plays": "3.1M",
                "duration": "0:32",
                "published": "5 hours ago",
                "url": "https://www.instagram.com/explore/tags/reels/",
                "thumbnail": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=800&q=80",
                "score": 95,
            },
            {
                "title": "Luxury Cinematic B-Roll Ideas for Viral Reels",
                "hindi_topic": "वायरल रील्स के लिए लग्ज़री सिनेमैटिक बी-रोल आइडियाज",
                "creator": "@cinecraftdaily",
                "plays": "2.4M",
                "duration": "0:27",
                "published": "9 hours ago",
                "url": "https://www.instagram.com/explore/tags/cinematicreels/",
                "thumbnail": "https://images.unsplash.com/photo-1492691527719-9d1e07e534b4?auto=format&fit=crop&w=800&q=80",
                "score": 91,
            },
            {
                "title": "Viral Fitness Transformation Reel Formula",
                "hindi_topic": "वायरल फिटनेस ट्रांसफॉर्मेशन रील फॉर्मूला",
                "creator": "@fitframes",
                "plays": "1.8M",
                "duration": "0:24",
                "published": "12 hours ago",
                "url": "https://www.instagram.com/explore/tags/fitnessreels/",
                "thumbnail": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&w=800&q=80",
                "score": 88,
            },
        ]

    def scrape_youtube_viral_videos(self) -> List[TrendingTopic]:
        """Auto-collect viral YouTube video ideas with safe fallback data."""
        try:
            logger.info("Collecting viral YouTube videos")
            api_key = os.getenv("YOUTUBE_API_KEY")
            items: List[Dict] = []

            if api_key:
                try:
                    params = {
                        "part": "snippet",
                        "chart": "mostPopular",
                        "regionCode": os.getenv("YOUTUBE_REGION", "IN"),
                        "maxResults": 10,
                        "videoCategoryId": "0",
                        "key": api_key,
                    }
                    response = self.session.get(
                        "https://www.googleapis.com/youtube/v3/videos",
                        params=params,
                        timeout=15,
                    )
                    response.raise_for_status()
                    data = response.json()

                    for item in data.get("items", []):
                        snippet = item.get("snippet", {})
                        title = snippet.get("title", "Untitled Viral Video")
                        items.append({
                            "title": title,
                            "hindi_topic": f"{title} पर हिंदी वीडियो आइडिया",
                            "channel": snippet.get("channelTitle", "Unknown Channel"),
                            "views": "Hot",
                            "duration": "Short",
                            "published": snippet.get("publishedAt", "recently"),
                            "url": f"https://www.youtube.com/watch?v={item.get('id', '')}",
                            "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                            "score": 92,
                        })
                except Exception as api_error:
                    logger.warning(f"YouTube API fetch failed, using fallback dataset: {api_error}")

            if not items:
                items = self._youtube_fallback_items()

            topics: List[TrendingTopic] = []
            for item in items:
                category_key = self._infer_category(item["title"])
                category_info = self.categories.get(category_key, self.categories["entertainment"])
                topics.append(
                    TrendingTopic(
                        topic=item["title"],
                        source="youtube_viral",
                        category=category_key,
                        hindi_category=category_info["hi"],
                        trending_score=float(item.get("score", 85)),
                        metadata={
                            "hindi_topic": item.get("hindi_topic", item["title"]),
                            "platform": "youtube",
                            "creator": item.get("channel", "Unknown Channel"),
                            "views": item.get("views", "N/A"),
                            "duration": item.get("duration", "Short"),
                            "published": item.get("published", "recently"),
                            "url": item.get("url"),
                            "thumbnail": item.get("thumbnail"),
                            "content_type": "viral_video",
                        },
                        created_at=datetime.now(),
                    )
                )

            logger.info(f"Found {len(topics)} viral YouTube video ideas")
            return topics
        except Exception as e:
            logger.error(f"Error collecting viral YouTube videos: {str(e)}")
            return []

    def scrape_instagram_trending_reels(self) -> List[TrendingTopic]:
        """Auto-collect trending Instagram reels with safe fallback data."""
        try:
            logger.info("Collecting Instagram trending reels")
            items = self._instagram_fallback_items()

            topics: List[TrendingTopic] = []
            for item in items:
                category_key = self._infer_category(item["title"])
                category_info = self.categories.get(category_key, self.categories["entertainment"])
                topics.append(
                    TrendingTopic(
                        topic=item["title"],
                        source="instagram_reels",
                        category=category_key,
                        hindi_category=category_info["hi"],
                        trending_score=float(item.get("score", 84)),
                        metadata={
                            "hindi_topic": item.get("hindi_topic", item["title"]),
                            "platform": "instagram",
                            "creator": item.get("creator", "@unknown"),
                            "views": item.get("plays", "N/A"),
                            "duration": item.get("duration", "Short"),
                            "published": item.get("published", "recently"),
                            "url": item.get("url"),
                            "thumbnail": item.get("thumbnail"),
                            "content_type": "trending_reel",
                        },
                        created_at=datetime.now(),
                    )
                )

            logger.info(f"Found {len(topics)} trending Instagram reels")
            return topics
        except Exception as e:
            logger.error(f"Error collecting Instagram reels: {str(e)}")
            return []
    
    def collect_all_trending_topics(self) -> List[TrendingTopic]:
        """
        Collect trending topics from all sources
        
        Returns:
            List of all trending topics
        """
        try:
            logger.info("Collecting trending topics from all sources")
            
            all_topics = []
            
            # Collect from all sources
            all_topics.extend(self.scrape_youtube_trending())
            all_topics.extend(self.scrape_youtube_viral_videos())
            all_topics.extend(self.scrape_instagram_trending_reels())
            all_topics.extend(self.scrape_google_trends())
            all_topics.extend(self.scrape_twitter_trending())
            all_topics.extend(self.scrape_news_headlines())
            
            logger.info(f"Collected total {len(all_topics)} trending topics")
            
            # Remove duplicates and sort by trending score
            unique_topics = self._remove_duplicates(all_topics)
            sorted_topics = sorted(unique_topics, key=lambda x: x.trending_score, reverse=True)
            
            return sorted_topics
            
        except Exception as e:
            logger.error(f"Error collecting trending topics: {str(e)}")
            return []
    
    def _remove_duplicates(self, topics: List[TrendingTopic]) -> List[TrendingTopic]:
        """
        Remove duplicate topics based on similarity
        
        Args:
            topics: List of trending topics
            
        Returns:
            List of unique topics
        """
        try:
            unique_topics = []
            seen_topics = set()
            
            for topic in topics:
                # Create a normalized version of topic for comparison
                normalized_topic = self._normalize_topic(topic.topic)
                
                if normalized_topic not in seen_topics:
                    seen_topics.add(normalized_topic)
                    unique_topics.append(topic)
            
            return unique_topics
            
        except Exception as e:
            logger.error(f"Error removing duplicates: {str(e)}")
            return topics
    
    def _normalize_topic(self, topic: str) -> str:
        """
        Normalize topic string for comparison
        
        Args:
            topic: Topic string
            
        Returns:
            Normalized topic string
        """
        try:
            # Convert to lowercase
            normalized = topic.lower()
            
            # Remove special characters and extra spaces
            normalized = re.sub(r'[^a-z0-9\s]', '', normalized)
            normalized = re.sub(r'\s+', ' ', normalized)
            
            # Remove common words
            common_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for']
            words = normalized.split()
            filtered_words = [word for word in words if word not in common_words]
            
            return ' '.join(filtered_words)
            
        except Exception as e:
            logger.error(f"Error normalizing topic: {str(e)}")
            return topic
    
    def get_top_topics(self, limit: int = 10, categories: Optional[List[str]] = None) -> List[TrendingTopic]:
        """
        Get top trending topics
        
        Args:
            limit: Maximum number of topics to return
            categories: Filter by categories
            
        Returns:
            List of top trending topics
        """
        try:
            all_topics = self.collect_all_trending_topics()
            
            # Filter by categories if specified
            if categories:
                all_topics = [topic for topic in all_topics if topic.category in categories]
            
            # Return top N topics
            return all_topics[:limit]
            
        except Exception as e:
            logger.error(f"Error getting top topics: {str(e)}")
            return []
    
    def save_topics(self, topics: List[TrendingTopic], filename: str):
        """
        Save topics to JSON file
        
        Args:
            topics: List of trending topics
            filename: Output filename
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(
                    [{
                        "topic": topic.topic,
                        "hindi_topic": topic.metadata.get("hindi_topic", topic.topic),
                        "source": topic.source,
                        "category": topic.category,
                        "hindi_category": topic.hindi_category,
                        "trending_score": topic.trending_score,
                        "metadata": topic.metadata
                    } for topic in topics],
                    f,
                    ensure_ascii=False,
                    indent=2
                )
            
            logger.info(f"Topics saved to {filename}")
            
        except Exception as e:
            logger.error(f"Error saving topics: {str(e)}")

# Test function
def test_scraper():
    """Test the scraper"""
    scraper = HindiTrendingScraper()
    
    # Get top 5 trending topics
    top_topics = scraper.get_top_topics(limit=5)
    
    print("=== TOP 5 TRENDING TOPICS ===")
    for i, topic in enumerate(top_topics, 1):
        print(f"{i}. {topic.topic}")
        print(f"   Hindi: {topic.metadata.get('hindi_topic', topic.topic)}")
        print(f"   Category: {topic.hindi_category} ({topic.category})")
        print(f"   Score: {topic.trending_score}")
        print(f"   Source: {topic.source}")
        print()
    
    # Save topics
    scraper.save_topics(top_topics, "trending_topics.json")
    print("Topics saved to trending_topics.json")

if __name__ == "__main__":
    test_scraper()