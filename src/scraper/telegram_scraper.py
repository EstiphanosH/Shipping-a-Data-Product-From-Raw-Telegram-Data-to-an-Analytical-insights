import os
import json
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from .utils import ensure_directory_exists

# Load environment variables
load_dotenv()

class TelegramScraper:
    def __init__(self):
        self.api_id = os.getenv('API_ID')
        self.api_hash = os.getenv('API_HASH')
        self.session_name = os.getenv('SESSION_NAME')
        self.phone = os.getenv('PHONE')
        self.channels = os.getenv('CHANNELS').split(',')
        self.client = None
        self.logger = self.setup_logger()

    def setup_logger(self):
        logger = logging.getLogger('telegram_scraper')
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler('logs/scraper.log')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    async def start_client(self):
        self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
        await self.client.start(phone=self.phone)
        self.logger.info("Telegram client started")

    async def scrape_channel(self, channel, target_date):
        try:
            self.logger.info(f"Scraping channel: {channel}")
            messages = []
            entity = await self.client.get_entity(channel)
            
            async for message in self.client.iter_messages(entity, offset_date=target_date):
                if message.date.date() != target_date.date():
                    break
                messages.append({
                    'id': message.id,
                    'date': message.date.isoformat(),
                    'text': message.text,
                    'media': bool(message.media),
                    'channel': channel
                })
            
            return messages
        except FloodWaitError as e:
            self.logger.error(f"Flood wait error: {e.seconds} seconds")
            await asyncio.sleep(e.seconds)
            return await self.scrape_channel(channel, target_date)
        except Exception as e:
            self.logger.error(f"Error scraping {channel}: {str(e)}")
            return []

    async def run(self, days_back=1):
        await self.start_client()
        target_date = datetime.utcnow() - timedelta(days=days_back)
        date_str = target_date.strftime('%Y-%m-%d')
        
        for channel in self.channels:
            try:
                messages = await self.scrape_channel(channel, target_date)
                if messages:
                    self.save_messages(messages, channel, date_str)
                    self.logger.info(f"Saved {len(messages)} messages from {channel}")
            except Exception as e:
                self.logger.error(f"Failed to scrape {channel}: {str(e)}")
        
        await self.client.disconnect()

    def save_messages(self, messages, channel, date_str):
        sanitized_channel = channel.replace('/', '_')
        dir_path = f"data/raw/telegram_messages/{date_str}/{sanitized_channel}"
        ensure_directory_exists(dir_path)
        
        file_path = f"{dir_path}/messages.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)