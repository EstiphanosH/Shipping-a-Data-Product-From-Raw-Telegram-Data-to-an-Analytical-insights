import os
import json
import logging
from datetime import datetime, timedelta
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto
import aiofiles
import aiofiles.os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('telegram_scraper')

class TelegramScraper:
    def __init__(self, api_id, api_hash, session_name='session'):
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name
        self.client = TelegramClient(session_name, api_id, api_hash)
        self.data_root = os.getenv('DATA_ROOT', 'data')
        self.raw_data_dir = os.path.join(self.data_root, 'raw')
        self.channel_info = {}
        
    async def start(self):
        await self.client.start()
        logger.info("Telegram client started")

    async def scrape_channel(self, channel_url, days_back=30):
        """Scrape channel data and structure for star schema"""
        try:
            channel_entity = await self.client.get_entity(channel_url)
            await self._scrape_channel_info(channel_entity)
            await self._scrape_channel_messages(channel_entity, days_back)
            return True
        except Exception as e:
            logger.error(f"Error scraping {channel_url}: {str(e)}")
            return False

    async def _scrape_channel_info(self, channel_entity):
        """Scrape channel info for dim_channels dimension"""
        channel_data = {
            "channel_id": channel_entity.id,
            "channel_name": getattr(channel_entity, 'username', ''),
            "title": getattr(channel_entity, 'title', ''),
            "description": getattr(channel_entity, 'about', ''),
            "member_count": getattr(channel_entity, 'participants_count', 0),
            "created_at": channel_entity.date.isoformat() if hasattr(channel_entity, 'date') else None,
            "scraped_at": datetime.utcnow().isoformat()
        }
        
        # Save channel info
        channel_dir = os.path.join(self.raw_data_dir, 'telegram_channels')
        await aiofiles.os.makedirs(channel_dir, exist_ok=True)
        channel_file = os.path.join(channel_dir, f"{channel_data['channel_name']}.json")
        
        async with aiofiles.open(channel_file, 'w') as f:
            await f.write(json.dumps(channel_data, indent=2))
        
        self.channel_info[channel_entity.id] = channel_data
        logger.info(f"Saved channel info: {channel_data['channel_name']}")
        return channel_data

    async def _scrape_channel_messages(self, channel_entity, days_back):
        """Scrape messages for fct_messages fact table"""
        channel_name = getattr(channel_entity, 'username', str(channel_entity.id))
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)
        
        logger.info(f"Scraping messages from {channel_name} between {start_date} and {end_date}")
        
        messages = []
        async for message in self.client.iter_messages(
            channel_entity,
            offset_date=end_date,
            reverse=True
        ):
            if message.date < start_date:
                break
                
            if not message.message and not message.media:
                continue
                
            # Prepare message data for fct_messages
            message_data = {
                "message_id": message.id,
                "channel_id": channel_entity.id,
                "date_utc": message.date.isoformat(),
                "message_text": message.text or "",
                "views": message.views or 0,
                "forwards": message.forwards or 0,
                "has_media": bool(message.media),
                "media_type": None,
                "media_path": None,
                "scraped_at": datetime.utcnow().isoformat()
            }
            
            # Handle media files
            if isinstance(message.media, MessageMediaPhoto):
                message_data["media_type"] = "photo"
                media_path = await self._download_media(
                    message, 
                    channel_name,
                    message.date.date()
                )
                message_data["media_path"] = media_path
            
            messages.append(message_data)
            
            # Log progress
            if len(messages) % 50 == 0:
                logger.info(f"Scraped {len(messages)} messages from {channel_name}")
        
        # Save messages partitioned by date
        for date_str, daily_messages in self._group_messages_by_date(messages):
            date_dir = os.path.join(
                self.raw_data_dir,
                'telegram_messages',
                channel_name,
                date_str
            )
            await aiofiles.os.makedirs(date_dir, exist_ok=True)
            file_path = os.path.join(date_dir, f"{date_str}.json")
            
            async with aiofiles.open(file_path, 'w') as f:
                await f.write(json.dumps(daily_messages, indent=2))
                
            logger.info(f"Saved {len(daily_messages)} messages for {date_str} in {channel_name}")

    async def _download_media(self, message, channel_name, date):
        """Download media for object detection enrichment"""
        if not message.media:
            return None
            
        try:
            date_str = date.isoformat()
            media_dir = os.path.join(
                self.raw_data_dir,
                'telegram_media',
                channel_name,
                date_str
            )
            await aiofiles.os.makedirs(media_dir, exist_ok=True)
            
            file_path = os.path.join(media_dir, f"{message.id}.jpg")
            await self.client.download_media(message.media, file_path)
            return file_path
        except Exception as e:
            logger.error(f"Error downloading media for message {message.id}: {str(e)}")
            return None

    def _group_messages_by_date(self, messages):
        """Group messages by date for partitioning"""
        grouped = {}
        for message in messages:
            date_key = datetime.fromisoformat(message["date_utc"]).date().isoformat()
            if date_key not in grouped:
                grouped[date_key] = []
            grouped[date_key].append(message)
        return grouped.items()

    async def close(self):
        await self.client.disconnect()
        logger.info("Telegram client disconnected")